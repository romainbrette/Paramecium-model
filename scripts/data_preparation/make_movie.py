'''
Makes a high quality compressed mp4 movie from a tiff sequence (4 MB/s).
Runs recursively on a cluster using `parallel`.

Argument: folder name
'''
import imageio
import sys
import os
import yaml
from file_management.batch_processing import *
from file_management.configuration import *

default_fps = 30.

### Command line argument: path
path = sys.argv[1]

protocol_folder = os.path.split(os.path.split(path)[0])[0]
protocol_filename = os.path.join(protocol_folder,'protocol.yaml')

if os.path.exists(protocol_filename):
    print(protocol_filename)
    ### Get FPS from description file
    with open(protocol_filename) as f:
        fps = yaml.load(f).get('framerate', default_fps)

    ### Write file
    new_filename = path+'.mp4'

    file_list = [f.path for f in os.scandir(path) if f.name[-5:]=='.tiff']
    file_list.sort()

    writer = imageio.get_writer(new_filename, fps=fps, quality=None, bitrate=4000000*8) # 4 MB/s seems acceptable
    for file in file_list:
        image = imageio.imread(file)
        writer.append_data(image)
    writer.close()
else: # Not an image folder: look recursively for protocol folders
    ### Look for all protocol folders
    folders = protocol_folders(path, recursive=True)

    ### List all trials
    trial_folders = []
    for folder in folders:
        folder = os.path.join(folder,'images')
        if os.path.exists(folder):
            trial_folders.extend([f.path for f in os.scandir(folder) if f.name.isnumeric()])

    python = python_binary()  # I suppose it could be obtained otherwise

    cluster_batch(python_binary(), os.path.realpath(__file__), trial_folders)
