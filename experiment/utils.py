'''
A few useful function for experimental recording.
'''
import os
import shutil
from clampy import *
from glob import glob
import os
import time
import datetime
import numpy as np
import datetime
import yaml
import inspect
import imageio

__all__ = ['make_experimental_files', 'cell_folder', 'prepare_experiment',
           'preliminary_video']

def cell_folder(path, intercell_time = 10*60):
    '''
    Looks for the most recent folder in path.
    If the last file of that folder has been written
    more than `intercell_time` ago (in second), then make a new cell
    folder.
    '''
    path = os.path.expanduser(path)

    #new_folder_name = date_time()+' Cell'
    today = datetime.datetime.today()
    new_folder_name = '{:%Y-%m-%d %H.%M.%S} cell'.format(today)

    # Get all folders cell*
    folders = [(file, os.path.getmtime(file)) for file in glob(os.path.join(path,'*cell*')) if os.path.isdir(file)]

    if folders != []:
        # Look for the most recent one
        folders.sort(key=lambda u: u[1])
        last_folder = folders[-1]

        # If this was another day, then make a new folder cell 1
        if datetime.date.today() == datetime.date.fromtimestamp(last_folder[1]):
            # Look for the date of the last modified file in that folder
            #dates = [os.path.getmtime(file) for file in glob(os.path.join(last_folder[0],'*'), recursive=True)]
            # Save as above, but Python 2 compatible:
            all_files = []
            for root, _, files in os.walk(last_folder[0]):
                all_files.extend([os.path.join(root,file) for file in files])
            dates = [os.path.getmtime(file) for file in all_files]
            if dates == []: # no file
                last_modification = last_folder[1]
            else:
                last_modification = max(dates)
            interval = time.time()-last_modification
            if interval>intercell_time: # new cell
                # Make a new folder
                folder_name = os.path.join(path,new_folder_name)
                os.mkdir(folder_name)
                return folder_name
            else:
                return last_folder[0]

    # Make a new folder
    folder_name = os.path.join(path, new_folder_name)
    os.mkdir(folder_name)
    return folder_name

def make_experimental_files(path, script_name=None, name=None, intercell_time=10*60.):
    '''
    Use intercell_time = very large number to prevent making new cell folders.
    In that case, cell folders must be created manually with "cell" in the name.
    '''
    if script_name is None:
        # Get filename of calling script
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        script_name = module.__file__[:-14] # assuming it ends with _experiment.py

    if name is None:
        name = script_name

    # Make a data folder
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        os.mkdir(path)

    today = datetime.datetime.today() ## Better: take it from the path name
    cell_path = cell_folder(path, intercell_time=intercell_time)
    #if not os.path.exists(path):
    #    os.mkdir(path)
    #path = os.path.join(path,date_time()+' '+name)
    path = os.path.join(cell_path,'{:%Y-%m-%d %H.%M.%S} {}'.format(today,name))
    os.mkdir(path)
    # Copy current script and analysis script
    shutil.copy(script_name+'_experiment.py',path)
    shutil.copy(script_name+'_analysis.py',path)
    if not os.path.exists(os.path.join(cell_path,'notes.yaml')):
        with open('notes.yaml', 'r') as fp:
            notes = yaml.safe_load(fp)
        notes['date'] = today.isoformat()
        with open(os.path.join(cell_path,'notes.yaml'), 'w') as fp:
            yaml.dump(notes, fp)

    return path #, today

def prepare_experiment(path=None, camera=None, parameters=None):
    '''
    Common tasks for all experiments.
    '''
    if path is None:
        path = '~/Paramecium data'

    if camera is None:
        camera_parameters = None
    else:
        camera_parameters = camera.camera_parameters

    # Get filename of calling script
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    script_name = module.__file__[:-14] # assuming it ends with _experiment.py

    # Make folders and copy files
    path = make_experimental_files(path, script_name=script_name, name=parameters['name'])
    data_path = os.path.join(path,'electrophysiology')
    os.mkdir(data_path)
    if camera is not None:
        image_path = os.path.join(path, 'images')
        os.mkdir(image_path)
    else:
        image_path = None

    # Save info
    ## TODO: add information about board and amplifier
    save_info(path+'/protocol.yaml',
              camera_parameters=camera_parameters, date=datetime.datetime.today().isoformat(),
              **parameters)

    # Screenshot
    imageio.imwrite(path+'/screenshot.png', imageio.imread('<screen>'))

    return path, data_path, image_path

def preliminary_video(camera, path, trigger, board):
    print("First video")
    total_duration = len(trigger)/board.sampling_rate
    n_trigger = sum(trigger)
    print('Expecting {} images'.format(n_trigger))

    # Dummy video recording
    movie_dir = os.path.join(path, 'dummy')
    camera.record_sequence(float(total_duration) + .5, movie_dir, file_prefix='',
                           nimages=n_trigger)
    board.acquire('V1', trigger=trigger)
    camera.stop()
