'''
Fix anterior and posterior positions in the morphology file, based on PIV.
Anterior and posterior ends picked by eye are swapped to be consistent with swimming direction.
This requires prior PIV analysis.
'''
import numpy as np
from file_management import *
import sys
from scipy.stats import circmean
from os.path import join
import yaml

args = sys.argv
try:
    path = args[1]
except:
    path = '/Users/romainbrette/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV/2020-10-28 17.46.05 cell'

run_this_on_all_cells(path)

# Load morphology measurement
with open(join(path, 'morphology.yaml')) as f:
    d = yaml.safe_load(f)
x1, y1 = d['anterior']
x2, y2 = d['posterior']

# Load PIV data
piv = load_multiple_data(path,'piv_analysis/analysis')
angle = piv['angle_mean'][:,:3].flatten() # use the first 3 frames to calculate piv angle
angle0 = circmean(angle[~np.isnan(angle)], np.pi, -np.pi)
cell_angle = -np.arctan2(y2-y1,x2-x1)
if np.cos(angle0 - cell_angle) < 0:
    x1, y1, x2, y2 = x2, y2, x1, y1
    print('Flipped',path)

# Save morphology measurement
d['anterior'] = [x1, y1]
d['posterior'] = [x2, y2]

with open(join(path, 'morphology.yaml'), 'w') as f:
    yaml.dump(d, f)
