'''
Figure 7.
Zoom on action potential.
Ionic current in the example, based on passive subtraction.
Estimation of calcium accumulation.
'''
from brian2 import *
from brian2.units.constants import faraday_constant as F
import yaml
from file_management import *
from pylab import *
import matplotlib.font_manager as fm
import os
from scipy.signal import butter, sosfilt
from fitting import *
from matplotlib import gridspec
from plotting import *

fontprops = fm.FontProperties(size=18)

width, height = 3, 4

volume = 1700*um**3
# Window of calcium entry
t1 = 1.9*ms
t2 = 6.3*ms

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated with PIV','2020-10-15 18.30.21 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
# Alignment of traces on V0 = -22 mV
data['v'] = align_traces(data['v'], -22*mV, data['t']<300*ms)
t, I, V = data['t']-300*ms, data['I'], data['v']
dt = t[1] - t[0]

# Load fit data
with open(os.path.join(path, 'fits/ciliated.yaml'), 'r') as f:
    description = yaml.load(f)
EL = eval(description['model']['constants']['EL'])
C = eval(description['model']['constants']['C'])
gL = eval(description['model']['constants']['gL'])

# Run model
Ie = run_model(description['model'], data)['Ie']

# Traces
cmap = cm.rainbow #cm.Purples
sos_I = butter(4, float(2000. * Hz), 'lp', fs=float(1 / dt), output='sos') # 4th order Butterworth filter
sos_V = butter(4, float(5000. * Hz), 'lp', fs=float(1 / dt), output='sos') # 4th order Butterworth filter

gs = gridspec.GridSpec(4, 1)
fig = figure('Action potential', (width,height))

n = len([x for x in I if mean(x[(t > 0 * ms) & (t < 100 * ms)])>0.05*nA and mean(x[(t > 0 * ms) & (t < 100 * ms)])<=5*nA])

ax_V = fig.add_subplot(gs[0:2, 0])
ax_current = fig.add_subplot(gs[2:4, 0])

i = 0
for Ii,Vi in zip(Ie,V):
    Imean = mean(Ii[(t > 0 * ms) & (t < 100 * ms)])
    if (Imean>1.5*nA) and (Imean<1.8*nA): # 300 pA for the small one, 600 pA for the large one
        print(Imean)
        # if i%2 == 0:
        filtered_V = sosfilt(sos_V, Vi / mV)
        Ires = C * diff(Vi) / dt - Ii[:-1] - gL*(EL-Vi[:-1])
        Ca = cumsum(Ires)/(2*F*volume)*dt
        filtered = sosfilt(sos_I, -Ires / nA)
        i0 = i
        break
    i +=1
color = cmap(1-(i+0.25*n)/(n+0.25*n))
#color = 'k'
ax_V.plot(t / ms, filtered_V, color=color, alpha=1)
ax_current.plot(t[:-1] / ms, filtered, color=color, alpha=1)

# Total calcium entry
print(max(Ca)/uM,min(Ca)/uM)
total_Ca = Ca[t[:-1]>=t2][0] - Ca[t[:-1]>t1][0]
print("Calcium entry:",total_Ca/uM,"uM")
ax_current.text(10,-1.5,r'$\Delta [Ca]_i =$ {} µM'.format(int(total_Ca/uM)))

ax_current.plot([-5,20],[0,0],'k--')
ind = (t[:-1]>=t1) & (t[:-1]<=t2)
ax_current.fill_between(t[:-1][ind] / ms, filtered[ind], 0*filtered[ind], color=color, alpha=0.5)

ax_V.spines['right'].set_visible(False)
ax_V.spines['top'].set_visible(False)

ax_current.spines['right'].set_visible(False)
ax_current.spines['top'].set_visible(False)

ax_V.set_ylabel('V (mV)')
ax_V.set_ylim(-25,20)
ax_V.set_xlim(-5,20)

ax_current.set_ylabel('I (nA)')
ax_current.set_ylim(-2.5,3.5)
ax_current.set_xlim(-5,20)
ax_current.set_xlabel('Time (ms)')

tight_layout()

savefig('fig4_zoom.png', dpi=300)

show()
