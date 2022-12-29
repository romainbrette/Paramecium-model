'''
Figure 8.
Example of reversal asynchrony between anterior and posterior side.
2020-10-12 16.08.21
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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import colors

fontprops = fm.FontProperties(size=18)

width, height = 4, 3.5

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated with PIV','2020-09-30 18.25.38 cell')

data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
dt = data['t'][1] - data['t'][0]
piv = load_multiple_data(path, 'local_piv_analysis/analysis')

# Get stimulus amplitudes
I = amplitudes(data, 300*ms, 400*ms)

# Angle relative to cell angle
angle0 = cell_orientation(path)
anterior = cos(piv['angle_mean_anterior'][(I>0.99*nA) & (I<5.01*nA), :] - angle0)
posterior = cos(piv['angle_mean_posterior'][(I>0.99*nA) & (I<5.01*nA), :] - angle0)

# Frame times
t, trigger = data['t'], data['trigger'][0]  # this could fail if no trigger
t = t-300*ms
trigger_times = t[trigger > 0]
frame_times = .5 * (trigger_times[:-1] + trigger_times[1:])

# Figure
fig = figure('Reversal asynchrony', (width,height))
ax_anterior = fig.add_subplot(211)
ax_posterior = fig.add_subplot(212)

plot_curves(ax_anterior, frame_times/ms, anterior[::-1,:])
plot_curves(ax_posterior, frame_times/ms, posterior[::-1,:])

ax_anterior.set_xlim(-50,600)
ax_anterior.set_ylim(-1,1)
ax_anterior.spines['right'].set_visible(False)
ax_anterior.spines['top'].set_visible(False)
ax_anterior.set_ylabel(r'cos $\alpha$')
ax_anterior.set_yticks([-1,0,1])

cmap = cm.rainbow
cbaxes = inset_axes(ax_anterior, width="3%", height="50%", loc='lower right')
plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(1, 5), cmap=cmap), cax=cbaxes, ticks = [1,3,5])

ax_posterior.set_xlim(-50,600)
ax_posterior.set_ylim(-1,1)
ax_posterior.spines['right'].set_visible(False)
ax_posterior.spines['top'].set_visible(False)
ax_posterior.set_xlabel('Time (ms)')
ax_posterior.set_ylabel(r'cos $\alpha$')
ax_posterior.set_yticks([-1,0,1])

tight_layout()

savefig('fig5_reversal_asynchrony_example.png', dpi=300)

show()
