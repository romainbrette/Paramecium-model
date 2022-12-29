'''
Fig. 8
Anterior vs. posterior reversal time.
'''
from brian2 import *
import yaml
from file_management import *
from pylab import *
import matplotlib.font_manager as fm
import os
from os.path import join
from fitting import *
from plotting import *
from scipy.stats import circmean, linregress
from scipy.stats import wilcoxon

fontprops = fm.FontProperties(size=18)

width, height = 3.5, 3.5

# Load data
root = config['root']
path = join(root, 'Ciliated with PIV')

filenames = [f.path for f in os.scandir(path) if os.path.isdir(f.path) and 'cell' in f.name]

data = rename_electrophysiology_data(load_multiple_data(filenames[0], 'electrophysiology/data'))
dt = data['t'][1] - data['t'][0]

reversal_anterior, reversal_posterior = [], []
for filename in filenames:
    print(filename)
    piv = load_multiple_data(filename, 'local_piv_analysis/analysis')

    # Select only trials with 1*nA<I<5*nA (strong pulses)
    stimulus_start, stimulus_end = stimulus_time(one_protocol(filename))
    I = amplitudes(data, stimulus_start, stimulus_end)
    select_trials(piv, (I > 0.99 * nA) & (I < 5.01 * nA))

    angle0 = cell_orientation(filename)

    # Angle relative to cell angle, then interpolate to the electrophysiology acquisition rate
    angle1 = piv['angle_mean_anterior']
    angle2 = piv['angle_mean_posterior']

    cell_angle_anterior = circmean(angle1[:,:3].flatten(), np.pi, -np.pi)
    cell_angle_posterior = circmean(angle2[:,:3].flatten(), np.pi, -np.pi)

    # Select recordings with no missed frames and with forward swimming angles less than 45° away from cell orientation
    if (isnan(angle1).sum() == 0) & (cos(cell_angle_anterior-angle0)>0.7) & (cos(cell_angle_posterior-angle0)>0.7): # deviation < 45°
        interpolated_anterior = interpolate_piv(data, angle1)
        interpolated_posterior = interpolate_piv(data, angle2)
        reversal_anterior.append([reversal_duration(angle - angle0, start = int(400 * ms / dt)) for angle in interpolated_anterior])
        reversal_posterior.append([reversal_duration(angle - angle0, start = int(400 * ms / dt)) for angle in interpolated_posterior])

reversal_anterior, reversal_posterior = np.array(reversal_anterior), np.array(reversal_posterior)

#print(((reversal_posterior-reversal_anterior)*dt).mean(axis = 1))
_, p = wilcoxon(reversal_posterior.flatten(),reversal_anterior.flatten(),alternative='greater')
print('Wilcoxon test: p =',p)

delay = reversal_posterior.flatten()-reversal_anterior.flatten()
print('Delay between anterior and posterior reversals:',delay.mean()*dt,'+-',delay.std()*dt)

# Figure

fig = figure('Anterior vs. posterior reversal time', (width,height))
ax = fig.add_subplot(111)

ax.plot([0,350], [0,350], 'k')
ax.plot(reversal_anterior.flatten() * dt * 1e3, reversal_posterior.flatten() * dt * 1e3, '.k')

# Regression
slope, intercept, _, _, _ = linregress(reversal_anterior.flatten(), reversal_posterior.flatten())

x = array([0,350])
ax.plot(x, intercept*float(dt)*1e3 + slope*x, 'k--')

ax.set_xlim(0,350)
ax.set_ylim(0,350)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_xlabel(r'Anterior reversal (ms)')
ax.set_ylabel(r'Posterior reversal (ms)')

tight_layout()

savefig('fig5_anterior_vs_posterior.png', dpi=300)

show()
