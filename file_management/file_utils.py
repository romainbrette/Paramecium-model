'''
Some tools for file management
'''
import os

__all__ = ['up_dir', 'make_subdir']

def up_dir(path):
    return os.path.split(path)[0]

def make_subdir(path, dir):
    folder = os.path.join(path, dir)
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder
