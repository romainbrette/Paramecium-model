'''
Loads data sets

magic_load_data: only useful for data with old formats.
'''
from brian2 import *
from clampy import *
import os
from .data_preparation import merge_data
from .file_utils import up_dir

__all__ = ['rename_electrophysiology_data', 'magic_load_data', 'load_multiple_data']

def load_multiple_data(path, name):
    '''
    Loads multiple datasets of the type path/xxx/name
    where name is yyy/zzz (e.g. electrophysiology/data)
    '''
    subfolder = up_dir(name)
    folders = [f.path for f in os.scandir(path) if os.path.exists(os.path.join(f.path, subfolder))]
    folders.sort()
    datasets = []
    for folder in folders:
        data = load_dataset(os.path.join(folder, name))
        if data is not None:
            datasets.append(data)
    return merge_data(datasets)

def rename_electrophysiology_data(data):
    '''
    Rename electrophysiology variables and give units.
    '''
    try:
        data['I'] = data.pop('Ic') * amp
    except:
        data['I'] = data.pop('Ic2') * amp
    data['v'] = data.pop('V1') * volt
    data['v2'] = data.pop('V2') * volt
    data['t'] = data['t']*second
    return data

def magic_load_data(path, copy_first=False, first_only=False, rename=True):
    '''
    Loads a data set by guessing the name and location of data files.

    Returns:
        * dictionary of arrays with units
    '''
    # Look for data folder
    # Pattern 1: xxx_experiment.py, xxxyy.txt.gz or .npz
    # Pattern 2: Pulses/pulses.npz
    name = None
    for f in os.scandir(path):
        if f.path[-14:]=='_experiment.py':
            name = f.path[:-14]
            break
    try:
        if name is not None: # Try loading
            data = load_dataset(name, copy_first=copy_first,first_only=first_only)
            if data is None:
                name = None
        if name is None:
            name = os.path.join(path,r'pulses')
            data = load_dataset(name, copy_first=copy_first,first_only=first_only)
            if data is None:
                name = None
        if name is None:
            name = os.path.join(path,r'Pulses/pulses')
            data = load_dataset(name, copy_first=copy_first,first_only=first_only)
    except Exception as err:
        raise Exception("Error loading "+name+" "+str(err))

    if rename:
        # Rename Ic, Ic2 -> I
        if 'Ic' in data:
            data['I'] = data['Ic']
            del data['Ic']
        if 'Ic2' in data:
            data['I'] = data['Ic2']
            del data['Ic2']
        # Rename V1 -> v, V2 -> v2
        if 'V1' in data:
            data['v'] = data['V1']
            del data['V1']
        if 'V2' in data:
            data['v2'] = data['V2']
            del data['V2']

    # Add units ### could in be in the yaml file
    if 't' in data:
        data['t'] = data['t']*second
    if 'I' in data:
        data['I'] = data['I']*amp
    if 'v' in data:
        data['v'] = data['v']*volt
    if 'v2' in data:
        data['v2'] = data['v2']*volt

    return data
