'''
Analyzes PIV to produce:
- (circular) mean angle (relative to field of view, not cell orientation)
- angle (circular) variance
- median velocity along cell axis

The argument is a protocol folder.
'''
import os
import numpy as np
from file_management.batch_processing import *
from file_management.configuration import *
import sys
from scipy.stats import circmean, circvar
from file_management.folder_information import cell_orientation

# Parse command line arguments
args = sys.argv
path = args[1]
piv_folder = os.path.join(path,'piv')

if os.path.exists(piv_folder):
    analysis_folder = os.path.join(path,'piv_analysis')
    if not os.path.exists(analysis_folder):
        os.mkdir(analysis_folder)

    ### Load morphology measurement
    cell_folder = os.path.split(path)[0]
    cell_angle = cell_orientation(cell_folder)

    ### Get all trials folders
    trials = [f.path for f in os.scandir(piv_folder) if f.name.isnumeric()]
    trials.sort()

    ### Go through all trials
    for i,trial in enumerate(trials):
        ### Get filenames
        u_files = [f.path for f in os.scandir(trial) if f.name[:10] == 'velocity_u']
        u_files.sort()
        v_files = [f.path for f in os.scandir(trial) if f.name[:10] == 'velocity_v']
        v_files.sort()

        ### Go through all frames
        angle_mean, angle_var, median_velocity = [], [], []
        for u_file, v_file in zip(u_files, v_files):
            if 'invalid' in u_file:
                angle_mean.append(np.nan)
                angle_var.append(np.nan)
                median_velocity.append(np.nan)
            else:
                # Load data
                u, v = np.loadtxt(u_file), np.loadtxt(v_file)

                # Circular statistics
                angle = np.arctan2(v, u)
                angle_mean.append(circmean(angle))
                angle_var.append(circvar(angle))

                # Median velocity along cell axis (projection)
                if cell_angle is not None:
                    velocity = np.sqrt(u * u + v * v)
                    median_velocity.append(np.median(velocity * np.cos(angle - cell_angle)))
        angle_mean, angle_var, median_velocity = np.array(angle_mean), np.array(angle_var), np.array(median_velocity)

        ### Save data
        target_file = os.path.join(analysis_folder,'analysis{:03}.txt.gz'.format(i))
        if cell_angle is not None:
            header = 'angle_mean angle_var median_velocity'
            M = np.vstack([angle_mean, angle_var, median_velocity]).T
        else:
            header = 'angle_mean angle_var'
            M = np.vstack([angle_mean, angle_var]).T
        np.savetxt(target_file, M, header=header, comments='')

else: # Not a protocol folder: look recursively for protocol folders
    ### Look for all protocol folders
    folders = protocol_folders(path, recursive=True)
    folders = [f for f in folders if os.path.exists(os.path.join(f,'piv'))]

    python = python_binary()  # I suppose it could be obtained otherwise

    cluster_batch(python_binary(), os.path.realpath(__file__), folders)
