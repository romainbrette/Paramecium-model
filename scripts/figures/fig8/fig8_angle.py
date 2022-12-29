'''
Figure 8.
Polar histogram of PIV angles for forward and backward swimming.
'''
from scipy.stats import circmean
from brian2 import *
from os.path import join
from fitting import *
import os
from fitting import *
from file_management import *

width, height = 2, 2

# Load PIV data
filenames = [f.path for f in os.scandir(join(config['root'], 'Ciliated with PIV')) if os.path.isdir(f.path) and 'cell' in f.name]

all_forward_angles = []
all_backward_angles = []

for filename in filenames:
    print(filename)

    data = rename_electrophysiology_data(load_multiple_data(filename, 'electrophysiology/data'))
    piv = load_multiple_data(filename, 'piv_analysis/analysis')

    # Select only trials with 1*nA<I<5*nA (strong pulses)
    stimulus_start, stimulus_end = stimulus_time(one_protocol(filename))
    I = amplitudes(data, stimulus_start, stimulus_end)
    select_trials(data, (I > -0.01 * nA) & (I < 5.01 * nA))
    select_trials(piv, (I > -0.01 * nA) & (I < 5.01 * nA))

    # Angle relative to cell angle, then interpolate to the electrophysiology acquisition rate
    angle = piv['angle_mean']
    cell_angle = corrected_cell_angle(cell_orientation(filename),
                                      angle[:, :3])  # use the first 3 frames to calculate piv angle

    # Trigger times
    t = data['t']
    trigger = data['trigger'][0]
    trigger_times = t[trigger > 0]
    frame_times = .5*(trigger_times[:-1]+trigger_times[1:])

    forward_angle = angle[:, frame_times < 300 * ms].flatten()
    backward_angle = angle[:, (frame_times > 350 * ms) & (frame_times < 400 * ms)].flatten()

    mean_forward_angle = circmean(forward_angle[~isnan(forward_angle)], pi, -pi)
    mean_backward_angle = circmean(backward_angle[~isnan(backward_angle)], pi, -pi)

    all_forward_angles.append(mean_forward_angle-cell_angle)
    all_backward_angles.append(mean_backward_angle - cell_angle)

# Anterior pointing at pi/2
all_forward_angles = (np.array(all_forward_angles)  - pi/2) % (2*pi)
all_backward_angles = (np.array(all_backward_angles) - pi/2)  % (2*pi)

# Plot
fig = figure('Ciliary angle', (width,height))
ax = fig.add_subplot(111, projection='polar')

bins_number = 20
width = 2 * np.pi / bins_number
bins = np.linspace(0.0, 2 * np.pi, bins_number + 1)

# Forward angles
n, _ = np.histogram(all_forward_angles, bins)
bars = ax.bar(bins[:bins_number], n, width=width, bottom=0.0, color='b', alpha=0.2)

# Backward angles
n, _ = np.histogram(all_backward_angles, bins)
bars = ax.bar(bins[:bins_number], n, width=width, bottom=0.0, color='r', alpha=0.2)

# Mean angles
mean_forward_angle = circmean(all_forward_angles, 0, 2*pi)
mean_backward_angle = circmean(all_backward_angles, 0, 2*pi)
print('Mean forward angle: {} deg'.format(mean_forward_angle*180/pi))
print('Mean backward angle: {} deg'.format(mean_backward_angle*180/pi))
ax.arrow(mean_forward_angle,0,0,4,head_width=0.2,head_length=1,color='b')
ax.arrow(mean_backward_angle,0,0,4,head_width=0.2,head_length=1,color='r')

ax.set_xticks([0,pi/4,pi/2,3*pi/4,pi, 5*pi/4, 3*pi/2, 7*pi/4])
ax.set_xticklabels(['','','anterior','','','','posterior',''])
ax.set_yticks([])

fig.tight_layout()

savefig('fig5_angle.png', dpi=300)

show()
