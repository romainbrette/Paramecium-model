'''
Figure 5.
Example of trace and fit
'''
from brian2 import *
import yaml
from file_management import *
from pylab import *
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.font_manager as fm
from matplotlib import colors
import os
from fitting import run_model
from scipy.signal import butter, sosfilt

fontprops = fm.FontProperties(size=18)

width, height = 6, 4
scale_bar = False

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated 4 mM KCl/2020-05-12 18.44.35 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
t, I, V = data['t']-280*ms, data['I'], data['v']

# Load fit data
with open(os.path.join(path, 'fits/hyperpolarized.yaml'), 'r') as f:
    description = yaml.load(f)
EK = eval(description['model']['constants']['EK'])
VKir = eval(description['model']['constants']['V_IKir'])

# Run model
Vfits = run_model(description['model'], data)['v']

dt = t[1] - t[0]

# Traces
cmap = cm.rainbow
cmap_r = cm.rainbow_r
sos = butter(4, float(4000. * Hz), 'lp', fs=float(1 / dt), output='sos') # 4th order Butterworth filter

fig = figure('Hyperpolarized responses', (width,height))

n = len([x for x in I if mean(x)<-0.05*nA]) # only the hyperpolarized responses
ax_data = plt.subplot(211)
i = 0
for Ii,Vi in zip(I,V):
    if mean(Ii)<-0.05*nA:
        # if i%2 == 0:
        filtered = sosfilt(sos, Vi / mV)
        ax_data.plot(t / ms, filtered, color=cmap(i/n), alpha=0.5)
        i+=1
ax_data.spines['right'].set_visible(False)
ax_data.spines['top'].set_visible(False)
ylabel('V (mV)')
xlim(0,160)
ylim(-130,-25)
cbaxes = inset_axes(ax_data, width="3%", height="50%", loc='lower right')
plt.colorbar(cm.ScalarMappable(norm=colors.Normalize(-4, 0), cmap=cmap_r), cax=cbaxes)
if scale_bar:
    ax_data.spines['bottom'].set_visible(False)
    ax_data.set_xticks([])
    scalebar = AnchoredSizeBar(ax_data.transData,
                               50, '50 ms', 'lower right',
                               #pad=0.1,
                               frameon=False)
                               #size_vertical=1,
                               #fontproperties=fontprops)
    ax_data.add_artist(scalebar)

ax_fit = plt.subplot(212)
i = 0
for Ii,Vfit in zip(I,Vfits):
    if mean(Ii)<-0.05*nA:
        # if i%2 == 0:
        ax_fit.plot(t / ms, Vfit / mV, color=cmap(i/n), alpha=0.5)
        i+=1
plot([0,160],[EK/mV,EK/mV],'k--')
plot([0,160],[VKir/mV,VKir/mV],'k--')

ax_fit.spines['right'].set_visible(False)
ax_fit.spines['top'].set_visible(False)

ylabel('V (mV)')
xlim(0,160)
ylim(-130,-25)

if scale_bar:
    ax_fit.spines['bottom'].set_visible(False)
    ax_fit.set_xticks([])
else:
    xlabel('Time (ms)')

tight_layout()

savefig('fig2_example.png', dpi=300)

show()
