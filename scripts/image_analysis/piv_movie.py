'''
Makes a movie from the PIV analysis.
Optional overwriting.
'''
import os
import imageio
import numpy as np
import yaml
from file_management.batch_processing import *
from file_management.configuration import *
import sys
import pylab
import uuid
from scipy.ndimage import median_filter

default_fps = 30.
overwrite = True

# Parse command line arguments
args = sys.argv
path = args[1]
new_filename = path + '.mp4'

description_filename = os.path.join(path, 'piv.yaml')

if os.path.exists(description_filename):
    ### Get FPS from description file
    with open(description_filename) as f:
        fps = 1/yaml.load(f).get('dt', 1/default_fps)

    ### Grid
    x, y = np.loadtxt(os.path.join(path, 'grid.txt.gz')).T
    x, y = np.meshgrid(x,y)

    ### Get filenames
    u_files= [f.path for f in os.scandir(path) if f.name[:10]=='velocity_u']
    u_files.sort()
    v_files= [f.path for f in os.scandir(path) if f.name[:10]=='velocity_v']
    v_files.sort()

    ### Make movie
    movie_out = imageio.get_writer(new_filename, fps=fps)

    # File with the current PIV image
    temp_filename = 'temp{}.png'.format(str(uuid.uuid4()))

    for u_file, v_file in zip(u_files, v_files):
        if not('invalid' in u_file):
            # Load
            u, v = np.loadtxt(u_file), np.loadtxt(v_file)

            # Filter for visualization
            u = median_filter(u, size=3)  # Median filter does *not* take nan correctly into account
            v = median_filter(v, size=3)

            # Make vector field image with pylab
            fig = pylab.figure(figsize=(10, 10))
            pylab.axis('off')
            ax = pylab.axes([0, 0, 1, 1], frameon=False)
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.invert_yaxis()
            ax.quiver(x, y, u, v)
            pylab.savefig(temp_filename)  # temporary file
            pylab.close()

        # Write figure to output movie (duplicated if invalid)
        if os.path.exists(temp_filename):
            image = imageio.imread(temp_filename)
            movie_out.append_data(image)

    movie_out.close()
    os.remove(temp_filename)


else: # Not a PIV folder: look recursively for protocol folders
    ### Look for all protocol folders
    folders = protocol_folders(path, recursive=True)

    ### List all trials
    trial_folders = []
    for folder in folders:
        folder = os.path.join(folder,'piv')
        if os.path.exists(folder):
            trial_folders.extend([f.path for f in os.scandir(folder) if f.name.isnumeric() and (overwrite or not(os.path.exists(f.path+'.mp4')))])

    python = python_binary()  # I suppose it could be obtained otherwise

    cluster_batch(python_binary(), os.path.realpath(__file__), trial_folders)
