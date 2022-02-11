'''
Manages the configuration file
'''
import os
import yaml

__all__ = ['data_folders', 'config', 'python_binary']

def load_configuration():
    with open(os.path.expanduser('~/.paramecium_model_fitting.yaml'), 'r') as fp:
        config = yaml.safe_load(fp)
    return config

def data_folders(year=None):
    if year is None:
        l = []
        for year in config['data_folders']:
            l.extend(data_folders(year))
        return l
    else:
        return [os.path.join(config['root'],folder) for folder in config['data_folders'][int(year)]]

def python_binary():
    return os.path.expanduser(config['python'])

config = load_configuration()
config['root'] = os.path.expanduser(config['root'])