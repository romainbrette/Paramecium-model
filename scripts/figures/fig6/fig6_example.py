'''
Figure 6.
Example of trace and fit
'''
from brian2 import *
import yaml
from file_management import *
from pylab import *
import matplotlib.font_manager as fm
import os
from fitting import run_model
from scipy.signal import butter, sosfilt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import colors

fontprops = fm.FontProperties(size=18)

width, height = 6, 4
scale_bar = False

# Load data
root = config['root']
path = os.path.join(root, 'Deciliated/2019-08-09 11.20.06 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
t, I, V = data['t']-280*ms, data['I'], data['v']

# Load fit data
with open(os.path.join(path, 'fits/deciliated_bell_p2.yaml'), 'r') as f:
    description = yaml.load(f)
VK = eval(description['model']['constants']['V_IK'])

# Run model
Vfits = run_model(description['model'], data)['v']

dt = t[1] - t[0]

# Traces
cmap = cm.rainbow
sos = butter(4, float(4000. * Hz), 'lp', fs=float(1 / dt), output='sos') # 4th order Butterworth filter

fig = figure('Depolarized responses', (width,height))

n = len([x for x in I if mean(x[(t > 20 * ms) & (t < 120 * ms)])>0.05*nA and mean(x[(t > 20 * ms) & (t < 120 * ms)])<=4*nA])
ax_data = plt.subplot(211)
i = 0
for Ii,Vi in zip(I,V):
    Imean = mean(Ii[(t > 20 * ms) & (t < 120 * ms)])
    if (Imean>0.05*nA) and (Imean<=4*nA):
        # if i%2 == 0:
        filtered = sosfilt(sos, Vi / mV)
        ax_data.plot(t / ms, filtered, color=cmap(i/n), alpha=0.5)
        i+=1
ax_data.spines['right'].set_visible(False)
ax_data.spines['top'].set_visible(False)
ylabel('V (mV)')
xlim(0,160)
ylim(-20,60)
cbaxes = inset_axes(ax_data, width="3%", height="50%", loc='upper right')
plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(0, 4), cmap=cmap), cax=cbaxes)

ax_fit = plt.subplot(212)
i = 0
for Ii,Vfit in zip(I,Vfits):
    Imean = mean(Ii[(t > 20 * ms) & (t < 120 * ms)])
    if (Imean>0.05*nA) and (Imean<=4*nA):
        # if i%2 == 0:
        ax_fit.plot(t / ms, Vfit / mV, color=cmap(i/n), alpha=0.5)
        i+=1
plot([0,160],[VK/mV,VK/mV],'k--')

ax_fit.spines['right'].set_visible(False)
ax_fit.spines['top'].set_visible(False)

xlabel('Time (ms)')
ylabel('V (mV)')
xlim(0,160)
ylim(-20,60)
tight_layout()

savefig('fig3_example.png', dpi=300)

show()
