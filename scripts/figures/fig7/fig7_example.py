'''
Figure 7.
Example of trace: V, I and cos(angle).
'''
from brian2 import *
import yaml
from file_management import *
from pylab import *
import matplotlib.font_manager as fm
import os
from scipy.signal import butter, sosfilt
from fitting import *
from plotting import *
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

fontprops = fm.FontProperties(size=18)

width, height = 5, 4

t1 = -50*ms
t2 = 300*ms

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated with PIV','2020-10-28 17.46.05 cell')
#path = os.path.join(root, 'Ciliated with PIV','2020-10-15 18.30.21 cell')
#path = os.path.join(root, 'Ciliated with PIV','2020-10-13 19.14.05 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
# Alignment of traces on V0 = -22 mV
data['v'] = align_traces(data['v'], -22*mV, data['t']<300*ms)

t, I, V = data['t']-300*ms, data['I'], data['v']
dt = t[1] - t[0]
piv = load_multiple_data(path,'piv_analysis/analysis')

# Angle relative to cell angle, then interpolate to the electrophysiology acquisition rate
angle = piv['angle_mean']
cell_angle = corrected_cell_angle(cell_orientation(path), angle[:,:3]) # use the first 3 frames to calculate piv angle
cos_angle = interpolate_piv(data, cos(angle-cell_angle))
angle = interpolate_piv(data, angle-cell_angle) - 2*np.pi

# Load fit data
with open(os.path.join(path, 'fits/ciliated.yaml'), 'r') as f:
    description = yaml.load(f)
EL = eval(description['model']['constants']['EL'])

# Traces
cmap = cm.rainbow
sos = butter(4, float(4000. * Hz), 'lp', fs=float(1 / dt), output='sos') # 4th order Butterworth filter

gs = gridspec.GridSpec(8, 1)
fig = figure('Example', (width,height))

n = len([x for x in I if mean(x[(t > 0 * ms) & (t < 100 * ms)])>0.05*nA and mean(x[(t > 0 * ms) & (t < 100 * ms)])<=5*nA])
ax_V = fig.add_subplot(gs[0:4, 0])
ax_I = fig.add_subplot(gs[4:6, 0])
# Broken axis for current
divider = make_axes_locatable(ax_I)
ax_I2 = divider.new_vertical(size="100%", pad=0.1)
fig.add_axes(ax_I2)

ax_angle = fig.add_subplot(gs[6:8, 0])
i = 0
ampli = []
curves_V = []
curves_I = []
curves_angle = []
for Ii,Vi,ai in zip(I,V,cos_angle):
    Imean = mean(Ii[(t > 0 * ms) & (t < 100 * ms)])
    if (Imean>0.001*nA) and (Imean<=5*nA):
        if i%3 == 0:
            ampli.append(Imean)
            filtered = sosfilt(sos, Vi / mV)
            curves_V.append(filtered)
            curves_I.append(Ii / nA)
            curves_angle.append(ai)
        i+=1

color = None # cm.Purples
shift = 0 # 0.25
plot_curves(ax_V, t/ms, curves_V, index = ampli, cmap=color, color_shift=shift)
plot_curves(ax_I, t/ms, curves_I, index = ampli, cmap=color, color_shift=shift)
plot_curves(ax_I2, t/ms, curves_I, index = ampli, cmap=color, color_shift=shift)
plot_curves(ax_angle, t/ms, curves_angle, index = ampli, cmap=color, color_shift=shift)

ax_V.spines['right'].set_visible(False)
ax_V.spines['top'].set_visible(False)
ax_V.spines['bottom'].set_visible(False)
ax_V.set_ylabel('V (mV)')
ax_V.set_xlim(t1/ms,t2/ms)
ax_V.set_ylim(-40,20)
ax_V.set_xticks([])

ax_I.spines['right'].set_visible(False)
ax_I.spines['top'].set_visible(False)
#ax_I.set_ylabel('I (nA)')
ax_I.set_xlim(t1/ms,t2/ms)
ax_I.set_xticks([])
ax_I.set_ylim(0,0.55)

ax_I2.spines['right'].set_visible(False)
ax_I2.spines['top'].set_visible(False)
ax_I2.spines['bottom'].set_visible(False)
ax_I2.set_ylabel('I (nA)')
ax_I2.set_xlim(t1/ms,t2/ms)
ax_I2.set_xticks([])
ax_I2.set_ylim(0.55,5)

# From https://matplotlib.org/examples/pylab_examples/broken_axis.html
d = .015  # how big to make the diagonal lines in axes coordinates
# arguments to pass to plot, just so we don't keep repeating them
kwargs = dict(transform=ax_I2.transAxes, color='k', clip_on=False)
ax_I2.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
kwargs.update(transform=ax_I.transAxes)  # switch to the bottom axes
ax_I.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal

ax_angle.spines['right'].set_visible(False)
ax_angle.spines['top'].set_visible(False)
ax_angle.set_ylabel(r'cos($\alpha$)')
ax_angle.set_xlim(t1/ms,t2/ms)
ax_angle.set_ylim(-1,1)
ax_angle.set_xlabel('Time (ms)')

ax_angle.plot([t1/ms,t2/ms],[0,0],'k--')

fig.tight_layout()

savefig('fig4_example.png', dpi=300)

show()
