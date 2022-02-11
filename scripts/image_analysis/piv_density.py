'''
Calculates the density of particles in a movie.
After background subtraction and filtering to enhance particles, the maximum intensity is calculated in each window of size 50 um.
The proportion of windows with intensity > 20% of unfiltered max background intensity is reported.
'''
import os
import numpy as np
from file_management import *
import sys
from os.path import join, splitext, split
import imageio
import yaml
from scipy.ndimage import gaussian_filter

args = sys.argv
try:
    path = args[1]
except:
    #path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 18.02.02 weak pulses'
    path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 17.56.58 normal pulses'

run_this_on_all_protocols(path)

default_pixel_size = 0.178 # in um
feature_size_um = 20
maximum_movement_um = 10
particle_size = 1. # in um, for preprocessing (filtering particles based on size; this is the sigma of the inner Gaussian)
window_size = 50. # in um
threshold = 0.2 # density threshold

# Make output folder
output_folder = join(path, 'piv_density')
if not (os.path.exists(output_folder)):
    try:
        os.mkdir(output_folder)
    except OSError:  # typically this folder exists: this can happen when another process just created it
        pass

# Get image folder for each trial
image_folder = join(path, 'images')
trial_folders = [f.path for f in os.scandir(image_folder) if f.name.isnumeric()]
trial_folders.sort()

# Get information (pixel size, morphology)
with open(join(path, 'protocol.yaml')) as f:
    d = yaml.load(f)
pixel_size = d.get('pixel_width', default_pixel_size)
feature_size = int(feature_size_um / pixel_size)  # in pixels
sigma = int(particle_size / pixel_size)
winsize = int(window_size / pixel_size)  # in pixels

for i, image_folder in enumerate(trial_folders):
    # Ordered list of all files
    files = [f.path for f in os.scandir(image_folder) if f.name[-5:]=='.tiff']
    files.sort()

    # Calculate background
    image = imageio.imread(files[0])*1.
    for f in files[1:]:
        image += imageio.imread(f)*1.
    background = image/len(files)
    max_intensity = background.max()

    h, w = image.shape
    h_cropped, w_cropped = winsize*int(h/winsize), winsize*int(w/winsize)
    nwindows = int(h/winsize)*int(w/winsize)

    # Calculate density
    p = []
    for file in files:
        frame = imageio.imread(file)
        subtracted = frame - background
        filtered = (gaussian_filter(subtracted, sigma, truncate=2) - gaussian_filter(subtracted, sigma * 1.6, truncate=2)) * 1.3 * sigma
        # Normalize
        filtered = filtered/max_intensity
        # Crop to multiple of window_size
        filtered = filtered[:h_cropped, :w_cropped]
        # Maximum in each bin
        m = filtered.reshape((winsize,winsize*nwindows)).T.reshape((nwindows,winsize*winsize)).max(axis=-1)
        # Mean in each bin
        #m = abs(filtered).reshape((winsize,winsize*nwindows)).T.reshape((nwindows,winsize*winsize)).mean(axis=-1)
        # Proportion above some threshold
        p.append((m>threshold).mean())

    # Save results
    output_filename = join(output_folder, 'piv_density{:05}.txt.gz'.format(i))
    M = np.array([p]).T
    header = 'density'
    np.savetxt(output_filename, M, header=header, comments='')

    if ((i+1)%10 == 0):
        print(i+1,'/',len(trial_folders))
