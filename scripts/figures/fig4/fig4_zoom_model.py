'''
Figure 4.
Zoom: predicted currents.
'''
from brian2 import *
import yaml
from file_management import *
from pylab import *
import matplotlib.font_manager as fm
import os
from fitting import *
from plotting import *
from matplotlib import gridspec

fontprops = fm.FontProperties(size=18)

width, height = 3, 2

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated with PIV','2020-10-15 18.30.21 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
t, I, V = data['t']-300*ms, data['I'], data['v']
dt = t[1] - t[0]

# Load fit data
with open(os.path.join(path, 'fits/ciliated.yaml'), 'r') as f:
    description = yaml.load(f)

# Run model
fits = run_model(description['model'], data)
ICa, IK, IKCa, Ie = fits['ICa_cilia'], fits['IK'], fits['IKCa_cilia'], fits['Ie']

# Traces
cmap = cm.rainbow #cm.Purples
fig = figure('Current predictions', (width,height))
ax = fig.add_subplot(111)

n = len([x for x in I if mean(x[(t > 0 * ms) & (t < 100 * ms)])>0.05*nA and mean(x[(t > 0 * ms) & (t < 100 * ms)])<=5*nA])

i = 0
for Ii in Ie:
    Imean = mean(Ii[(t > 0 * ms) & (t < 100 * ms)])
    if (Imean>1.5*nA) and (Imean<1.8*nA): # 300 pA for the small one, 600 pA for the large one
        print(Imean)
        break
    i +=1
color = cmap(1-(i+0.25*n)/(n+0.25*n))

ax.plot(t / ms, -ICa[i]/nA, color=color, alpha=1)
ax.plot(t / ms, -IK[i]/nA, color=color, alpha=1)
ax.plot(t / ms, -IKCa[i]/nA, color=color, alpha=1)
ax.plot(t / ms, 0*t, 'k--')

ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.set_ylabel('I (nA)')
ax.set_xlim(-5,20)
ax.set_ylim(-2.5,3.5)
ax.set_xlabel('Time (ms)')

fig.tight_layout()

savefig('fig4_zoom_model.png', dpi=300)

show()
