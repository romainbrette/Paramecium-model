'''
Track anterior and posterior ends.
The first frame of each trial is matched to subsequent frames.
Remember that "anterior" and "posterior" refer to two unidentified ends here; they could be posterior and anterior.
Results are saved in um, measured along the main axis and the normal axis.
'''
import os
import numpy as np
from file_management import *
import sys
from os.path import join, splitext, split
import imageio
import yaml
from skimage.registration import phase_cross_correlation
from scipy.ndimage import gaussian_filter

filter = True # filters out particles; quite slow

args = sys.argv
try:
    path = args[1]
except:
    path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 18.02.02 weak pulses'
    #path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 17.56.58 normal pulses'

run_this_on_all_protocols(path)

default_pixel_size = 0.178 # in um
feature_size_um = 20
maximum_movement_um = 10
particle_size = 1. # in um, for preprocessing (filtering particles based on size; this is the sigma of the inner Gaussian)

# Make output folder
output_folder = join(path, 'tracked_ends')
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
cell_folder = split(path)[0]
with open(join(cell_folder, 'morphology.yaml')) as f:
    d = yaml.load(f)
pixel_size = d.get('pixel_width', default_pixel_size)
feature_size = int(feature_size_um / pixel_size)  # in pixels
sigma = int(particle_size / pixel_size)
# y = 0 is the top
x1, y1 = d['anterior']
x2, y2 = d['posterior']
main_axis = np.array([x1 - x2, y1 - y2])  # main axis (vector)
main_axis = pixel_size * main_axis / np.linalg.norm(main_axis) # we multiply by pixel_size to get results in um
normal_axis = np.array([main_axis[1], -main_axis[0]])


# Template matching
def calculate_shift(x, y, frame):
    # Calculates the shift (vector) between the reference image and the frame
    shift, _, _ = phase_cross_correlation(reference_image[int(y - feature_size / 2):int(y + feature_size / 2),
                                          int(x - feature_size / 2):int(x + feature_size / 2)],
                                          frame[int(y - feature_size / 2):int(y + feature_size / 2),
                                          int(x - feature_size / 2):int(x + feature_size / 2)], upsample_factor=100)
    ys, xs = shift
    return np.array([xs, ys])


for i, image_folder in enumerate(trial_folders):
    # Ordered list of all files
    files = [f.path for f in os.scandir(image_folder) if f.name[-5:]=='.tiff']
    files.sort()

    anterior_x, anterior_y, posterior_x, posterior_y = [], [], [], []

    reference_image = imageio.imread(files[0])
    for file in files[1:]:
        frame = imageio.imread(file)

        # Filter
        if filter:
            frame = gaussian_filter(frame, sigma*1.6, truncate=2)

        # Anterior
        displacement = calculate_shift(x1, y1, frame)
        # Project on cell axes
        anterior_x.append(np.dot(displacement, normal_axis))
        anterior_y.append(np.dot(displacement, main_axis))

        # Posterior
        displacement = calculate_shift(x2, y2, frame)
        posterior_x.append(np.dot(displacement, normal_axis))
        posterior_y.append(np.dot(displacement, main_axis))

    # Save results
    output_filename = join(output_folder, 'tracked_ends{:05}.txt.gz'.format(i))
    M = np.array([anterior_x, anterior_y, posterior_x, posterior_y]).T
    header = 'anterior_x anterior_y posterior_x posterior_y'
    np.savetxt(output_filename, M, header=header, comments='')

    if ((i+1)%10 == 0):
        print(i+1,'/',len(trial_folders))
