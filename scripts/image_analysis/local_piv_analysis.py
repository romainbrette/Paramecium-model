'''
Calculates the mean angle near the anterior and posterior ends.
Here the mean angle is calculated on the half-plane beyond the anterior/posterior ends.
'''
import os
import numpy as np
from file_management.batch_processing import *
from file_management.configuration import *
import sys
from scipy.stats import circmean, circvar
from file_management.folder_information import cell_orientation
from os.path import join, split
import yaml
from scipy.ndimage import median_filter

args = sys.argv
try:
    path = args[1]
except:
    #path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 18.02.02 weak pulses'
    #path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell/2020-10-28 17.56.58 normal pulses'
    path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-09-30 20.02.11 cell/2020-09-30 20.04.00 normal pulses'

run_this_on_all_protocols(path)

default_pixel_size = 0.178 # in um

piv_folder = os.path.join(path,'piv')

analysis_folder = os.path.join(path, 'local_piv_analysis')
if not os.path.exists(analysis_folder):
    os.mkdir(analysis_folder)

### Load morphology measurement
cell_folder = split(path)[0]
with open(join(cell_folder, 'morphology.yaml')) as f:
    d = yaml.load(f)
pixel_size = d.get('pixel_width', default_pixel_size)
# y = 0 is the top
x1, y1 = d['anterior']
x2, y2 = d['posterior']

### Get all trials folders
trials = [f.path for f in os.scandir(piv_folder) if f.name.isnumeric()]
trials.sort()

### Get grid coordinates
x, y = np.loadtxt(os.path.join(trials[0],'grid.txt.gz')).T # in pixels
x, y = np.meshgrid(x, y)
# Select zones beyond ends
ux, uy = (x1-x2), (y1-y2)
selection1 = ((x-x1)*ux + (y-y1)*uy)>0
selection2 = ((x-x2)*ux + (y-y2)*uy)<0

### Go through all trials
all1 = []
all2 = []
for i,trial in enumerate(trials):
    ### Get filenames
    u_files = [f.path for f in os.scandir(trial) if f.name[:10] == 'velocity_u']
    u_files.sort()
    v_files = [f.path for f in os.scandir(trial) if f.name[:10] == 'velocity_v']
    v_files.sort()

    ### Go through all frames
    angle_mean1, angle_mean2 = [], []
    for u_file, v_file in zip(u_files, v_files):
        if 'invalid' in u_file:
            angle_mean1.append(np.nan)
            angle_mean2.append(np.nan)
        else:
            # Load data
            u, v = np.loadtxt(u_file), np.loadtxt(v_file)

            # Smooth the field
            #u = median_filter(u, size=3)  # Median filter does *not* take nan correctly into account
            #v = median_filter(v, size=3)

            # Circular statistics
            angle1 = np.arctan2(v[selection1], u[selection1])
            angle_mean1.append(circmean(angle1))
            angle2 = np.arctan2(v[selection2], u[selection2])
            angle_mean2.append(circmean(angle2))

    angle_mean1, angle_mean2 = np.array(angle_mean1), np.array(angle_mean2)
    all1.append(angle_mean1)
    all2.append(angle_mean2)

    ### Save data
    target_file = os.path.join(analysis_folder,'analysis{:03}.txt.gz'.format(i))
    header = 'angle_mean_anterior angle_mean_posterior'
    M = np.vstack([angle_mean1, angle_mean2]).T
    np.savetxt(target_file, M, header=header, comments='')
