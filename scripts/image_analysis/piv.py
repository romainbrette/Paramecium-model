'''
PIV analysis
(Particle Image Velocimetry)

Calculates PIV vector fields from images.
Data are saved as .txt.gz files.
If the piv folder exists, skips.

Uses openpiv 0.21.2 (doesn't seem to be working with the newest version!)

!!! Note: in openpiv 0.21.2, y is flipped (y[::-1]), in later versions it's not...

TODO:
- Analysis from mp4 movies instead of TIFF
- could be refactored with make_movie
'''
import openpiv.process
import os
import imageio
import numpy as np
from scipy.ndimage import gaussian_filter
import yaml
from file_management.batch_processing import *
from file_management.configuration import *
import sys

# Parse command line arguments
args = sys.argv
path = args[1]
#print(path)

#### Parameters
window_size = 50. # in um
max_velocity = 200. # in um/s, particle velocity
particle_size = 1. # in um, for preprocessing (filtering particles based on size; this is the sigma of the inner Gaussian)
default_pixel_size = 0.178 # in um
default_fps = 30.

#### Openpiv version check
# 0.21.8 is new, 0.21.2 is old ; the old version inverts the y axis, not the new one
y = openpiv.process.get_coordinates(image_size=(2,1), window_size=1, overlap=0)[1]
openpiv_is_old = (y[0] == 1.5) # should be 0.5 if recent

### Check whether this is an image file in a protocol
parent = os.path.split(os.path.split(path)[0])[0]
protocol_file = os.path.join(parent, 'protocol.yaml')

if os.path.exists(protocol_file):
    #### Output folder
    # Target folder is path/../../piv/xxx where xxx is the folder name (extracted from path).
    piv_folder = os.path.join(parent,'piv')
    if not(os.path.exists(piv_folder)):
        try:
            os.mkdir(piv_folder)
        except OSError: # typically this folder exists: this can happen when another process just created it
            pass
    folder_name = os.path.split(path)[1]
    target = os.path.join(piv_folder,folder_name)
    if not(os.path.exists(target)):
        os.mkdir(target)

    #### Get dt and pixel size from description file

    # Find the frame rate in the protocol yaml file
    dt, pixel_size = None, None
    with open(protocol_file) as f:
        d = yaml.load(f)
        try:
            dt = 1./d['framerate'] # This is the dt of images, not of electrophysiology
        except KeyError:
            pass
        try:
            pixel_size = d['camera_parameters']['pixel_width']
        except KeyError:
            pass

    if pixel_size is None:
        print('{}: pixel size undefined'.format(path))
        pixel_size = default_pixel_size
    if dt is None:
        print('{}: Frame rate undefined'.format(path))
        dt = 1./default_fps

    #### Calculate preprocessing and PIV parameters
    sigma = int(particle_size / pixel_size)
    winsize = int(window_size / pixel_size)  # in pixels
    max_displacement = int(max_velocity * dt / pixel_size)  # in pixel
    searchsize = winsize + 2 * max_displacement
    overlap = int(winsize * 2 / 3)  # pixels

    #### Ordered list of all files
    files = [f.path for f in os.scandir(path) if f.name[-5:]=='.tiff']
    files.sort()

    #### Calculate grid
    image = imageio.imread(files[0])*1.
    x, y = openpiv.process.get_coordinates(image_size=image.shape, window_size=winsize, overlap=overlap)
    if openpiv_is_old:
        y = y[::-1]

    #### Write parameters
    d = {"window_size" : window_size,
         "max_velocity" : max_velocity,
         "particle_size" : particle_size,
         "dt" : dt,
         "pixel_size" : pixel_size}
    with open(os.path.join(target,'piv.yaml'), 'w') as f:
        yaml.dump(d, f)

    #### Save x, y
    np.savetxt(os.path.join(target,'grid.txt.gz'), np.vstack([x[0,:],y[:,0]]).T)

    #### Calculate background
    for f in files[1:]:
        image += imageio.imread(f)*1.
    background = image/len(files)

    #### Compute vector fields on image pairs
    previous_frame = None
    nrows, ncols = x.shape
    frame_i = 0
    previous_missed, invalid = False, False
    for file in files:
        frame = imageio.imread(file)
        # Preprocessing: remove background, filter particles with double Gaussian
        subtracted = frame - background
        filtered = (gaussian_filter(subtracted, sigma, truncate=2) - gaussian_filter(subtracted, sigma * 1.6, truncate=2)) * 1.3 * sigma

        # Turn to int (apparently necessary for the PIV algorithm)
        frame = (filtered * 32768).astype('int32')

        # Check missed frame
        if (frame == previous_frame).all():
            #print('Missed frame') # This frame is invalid and the next one as well
            # In principle we could use the next one, but then the calculated displacement would correspond to a larger time interval
            invalid = True
            previous_missed = True
        elif previous_missed:
            invalid = True
            previous_missed = False
        else:
            invalid = False
            previous_missed = False

        if previous_frame is not None:
            if invalid:
                # Creates empty file
                f = open(os.path.join(target, 'velocity_u{:05}_invalid.txt.gz'.format(frame_i)),'w')
                f.close()
                f = open(os.path.join(target, 'velocity_v{:05}_invalid.txt.gz'.format(frame_i)),'w')
                f.close()
            else:
                # Calculate vector field by cross-correlation
                u, v, sig2noise = openpiv.process.extended_search_area_piv(previous_frame, frame, window_size=winsize,
                                                                           overlap=overlap, dt=dt, search_area_size=searchsize,
                                                                           sig2noise_method='peak2peak')
                # Scaling to um/s
                u, v = u * pixel_size, v * pixel_size

                # Save to file
                np.savetxt(os.path.join(target, 'velocity_u{:05}.txt.gz'.format(frame_i)), u)
                np.savetxt(os.path.join(target, 'velocity_v{:05}.txt.gz'.format(frame_i)), v)

        previous_frame = frame.copy()
        frame_i += 1
else:  # Not an image folder: look recursively for protocol folders
    ### Look for all protocol folders
    folders = protocol_folders(path, recursive=True)

    ### List all trials
    trial_folders = []
    for folder in folders:
        image_folder = os.path.join(folder,'images')
        piv_folder = os.path.join(folder,'piv')
        if os.path.exists(image_folder) and not (os.path.exists(piv_folder)):
            trial_folders.extend([f.path for f in os.scandir(image_folder) if f.name.isnumeric()])

    python = python_binary()  # I suppose it could be obtained otherwise

    print(len(trial_folders),'image folders')

    cluster_batch(python_binary(), os.path.realpath(__file__), trial_folders)
