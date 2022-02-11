'''
Batch processing: applies a script on multiple files recursively.

Parallel running on cluster uses GNU Parallel.
There must be a configuration file named `~/.parallel/cluster`.
Example file:

-j 50%
-S slave1
-S slave2
-S slave3
--progress
--wd .
'''
import os
import subprocess
import time
from .configuration import *
import inspect

__all__ = ['batch', 'cell_folders', 'protocol_folders', 'cluster_batch', 'one_protocol',
           'run_this_on_all_cells', 'run_this_on_all_protocols', 'is_cell_folder', 'is_protocol_folder']

def is_cell_folder(folder):
    '''
    True if folder is a cell folder.
    '''
    name = os.path.split(folder)[1]
    return ('Cell' in name) or ('cell' in name)

def is_protocol_folder(folder):
    found = False
    for f in os.scandir(folder):
        if (f.path[-13:] == 'experiment.py') or (f.name == 'protocol.yaml'):  # experimental script
            found = True
            break
    return found

def cell_folders(*folders, recursive = False):
    '''
    Returns all cell folders in the paths given as arguments.
    '''
    cells = []
    for path in folders:
        if is_cell_folder(path):
            cells.append(path)
        if recursive:
            cells.extend(cell_folders(*[f.path for f in os.scandir(path) if os.path.isdir(f)\
                                              and ('Cell' not in f.name) and ('cell' not in f.name)], recursive=True))
        cells.extend(
            [f.path for f in os.scandir(path) if os.path.isdir(f) and (('Cell' in f.name) or ('cell' in f.name))])
    return cells

def one_protocol(folder):
    '''
    Returns the path of one protocol in the cell folder.
    '''
    for f in os.scandir(folder):
        if os.path.exists(os.path.join(f.path, 'protocol.yaml')):
            return f.path
    return None

def protocol_folders(*folders, recursive = False):
    '''
    Returns all protocol folders in the paths given as arguments.

    First looks for cell folders, and protocols inside the folders.
    A protocol folder is a folder with a file ending with "experiment.py" or a "protocol.yaml" file.
    '''
    cells = cell_folders(*folders, recursive=recursive)
    protocol_folders = cells.copy()
    for path in cells:
        protocol_folders.extend([f.path for f in os.scandir(path) if os.path.isdir(f)])

    # Check if there is an experimental script (...experiment.py)
    selection = []
    for folder in protocol_folders:
        found = False
        for f in os.scandir(folder):
            if (f.path[-13:] == 'experiment.py') or (f.name == 'protocol.yaml'): # experimental script
                found = True
                break
        if found: # it's a protocol folder
            selection.append(folder)

    return selection

def batch(script_name, folders, filter=None, n_processes = 5, verbose=True, recursive=False, args=[]):
    '''
    Calls `script_name` on each of the folders recursively, with a filter condition.
    '''
    if filter is None:
        filter = lambda d: True
    if isinstance(folders,str):
        folders = [folders]

    if recursive:
        # Walk through all subfolders
        valid_folders = []
        for folder in folders:
            for root, dirs, files in os.walk(folder):
                for dir in dirs:
                    filename = os.path.join(root, dir)
                    if filter(filename):
                        valid_folders.append(filename)
                        if verbose:
                            print(filename)
                #valid_folders.extend([os.path.join(root, dir) for dir in dirs if filter(dir)])
    else:
        valid_folders = [folder for folder in folders if filter(folder)]

    # Check
    print(len(valid_folders), 'folders')
    i = 0

    processes = [subprocess.Popen(['python','-W','ignore',script_name,filename]+args) for filename in
                 valid_folders[i:i + n_processes]]
    i += n_processes

    n_successful = 0
    while len(processes)>0:
        time.sleep(1)
        # Check if any process has finished
        return_codes = [process.poll() for process in processes]
        n_successful += return_codes.count(0)
        processes = [process for process, code in zip(processes,return_codes) if code is None] # Running processes
        # Add new processes
        if (len(processes)<n_processes) and (i<len(valid_folders)):
            n_new = n_processes-len(processes)
            processes.extend([subprocess.Popen(['python', '-W', 'ignore', script_name, filename] + args) for filename in
                         valid_folders[i:i + n_new]])
            i += n_new

    print('Ran successfully on {} folders'.format(n_successful))

# while i < len(valid_folders):
    #     processes = [subprocess.Popen(['python','-W','ignore',script_name,filename]+args) for filename in
    #                  valid_folders[i:i + n_processes]]
    #     # Then wait until all are finished
    #     for process in processes:
    #         process.wait()
    #     i += n_processes

def cluster_batch(python, script_name, folders, verbose=True, args=[]):
    '''
    Calls `script_name` on each of the folders using parallel, on a cluster.
    '''
    # First write the list of filenames to a file
    with open('filenames.txt', 'w') as f:
        f.write('\n'.join(folders))

    # Call parallel
    os.system('cat filenames.txt | parallel -Jcluster --joblog joblog.txt '+python+' -W ignore '+script_name+' {} '+' '.join(args))

def run_this_on_all_cells(path):
    '''
    The calling script is called on all cell folders below `path`, using `cluster_batch`.
    '''
    # frame = inspect.stack()[1]
    # module = inspect.getmodule(frame[0])
    # filename = module.__file__
    if not is_cell_folder(path):
        folders = cell_folders(path, recursive=True)

        # Get filename of calling script
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])

        cluster_batch(python_binary(), module.__file__, folders)
        exit(0)

def run_this_on_all_protocols(path):
    '''
    The calling script is called on all protocol folders below `path`.
    '''
    if not is_protocol_folder(path):
        folders = protocol_folders(path, recursive=True)

        # Get filename of calling script
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])

        cluster_batch(python_binary(), module.__file__, folders)
        exit(0)
