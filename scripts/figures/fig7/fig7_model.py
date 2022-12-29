'''
Figure 7.
Fit to the example.
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

width, height = 5, 7

t1 = -50*ms
t2 = 300*ms

# Load data
root = config['root']
path = os.path.join(root, 'Ciliated with PIV','2020-10-28 17.46.05 cell')
#path = os.path.join(root, 'Ciliated with PIV','2020-10-15 18.30.21 cell')
#path = os.path.join(root, 'Ciliated with PIV','2020-10-13 19.14.05 cell')
data = rename_electrophysiology_data(load_multiple_data(path, 'electrophysiology/data'))
t, I, V = data['t']-300*ms, data['I'], data['v']
dt = t[1] - t[0]

# Load fit data
with open(os.path.join(path, 'fits/ciliated.yaml'), 'r') as f:
    description = yaml.load(f)

# Parameters
params = description['model']['constants']
print(params)

pK_electromotor = params['pK_electromotor']
angle_min = params['angle_min']
angle_max = angle_min+params['angle_span']
n_electromotor = params['n_electromotor']
reversal_threshold = 0.1 * exp(pK_electromotor)
print('Reversal threshold:', reversal_threshold, 'µM')  # in uM

half_inactivation = 0.1 * exp(params['pKCa'])
print('Half inactivation:', half_inactivation, 'µM')  # in uM

KCa = 0.1 * exp(params['pKKCa'])
print('KCa:', KCa, 'µM')  # in uM

# Run model
fits = run_model(description['model'], data)
V, cos_angle, sin_angle, ICa, IK, IKCa, pCa = fits['v'], fits['cos_angle'], fits['sin_angle'], fits['ICa_cilia'], fits['IK'], fits['IKCa_cilia'], fits['pCa']
angle = np.arctan2(sin_angle, cos_angle)

# Traces
gs = gridspec.GridSpec(14, 1)
fig = figure('Fit', (width,height))

n = len([x for x in I if mean(x[(t > 0 * ms) & (t < 100 * ms)])>0.05*nA and mean(x[(t > 0 * ms) & (t < 100 * ms)])<=5*nA])
ax_V = fig.add_subplot(gs[0:4, 0])
ax_angle = fig.add_subplot(gs[4:6, 0])
ax_IK = fig.add_subplot(gs[8:10, 0])
ax_ICa_IKCa = fig.add_subplot(gs[6:8, 0])
ax_pCa = fig.add_subplot(gs[10:14, 0])
i = 0
Imean = array([mean(Ii[(t > 0 * ms) & (t < 100 * ms)]) for Ii in I])*amp
ind = [i for i,Ii in enumerate(Imean) if (Ii>0.001*nA) and (Ii<=5*nA) and (i%3 == 0)]

plot_curves(ax_V, t/ms, V[ind]/mV, index = Imean[ind]) #, cmap=cm.Reds, color_shift=0.25)
plot_curves(ax_angle, t/ms, cos_angle[ind], index = Imean[ind]) #, cmap=cm.Reds, color_shift=0.25)
plot_curves(ax_ICa_IKCa, t/ms, -ICa[ind]/nA, index = Imean[ind]) #, cmap=cm.Oranges, color_shift=0.25)
plot_curves(ax_IK, t/ms, -IK[ind]/nA, index = Imean[ind]) #, cmap=cm.Blues, color_shift=0.25)
plot_curves(ax_ICa_IKCa, t/ms, -IKCa[ind]/nA, index = Imean[ind])#, cmap=cm.Greys, color_shift=0.25) #Greens
plot_curves(ax_pCa, t/ms, exp(pCa[ind])*1e-7, index = Imean[ind]) #, cmap=cm.Reds, color_shift=0.25)

ax_V.spines['right'].set_visible(False)
ax_V.spines['top'].set_visible(False)
ax_V.spines['bottom'].set_visible(False)
ax_V.set_ylabel('V (mV)')
ax_V.set_xlim(t1/ms,t2/ms)
ax_V.set_ylim(-40,20)
ax_V.set_xticks([])

ax_angle.spines['right'].set_visible(False)
ax_angle.spines['top'].set_visible(False)
ax_angle.set_ylabel(r'cos($\alpha$)')
ax_angle.set_xlim(t1/ms,t2/ms)
ax_angle.set_ylim(-1,1)

ax_angle.plot([t1/ms,t2/ms],[0,0],'k--')

ax_ICa_IKCa.spines['right'].set_visible(False)
ax_ICa_IKCa.spines['top'].set_visible(False)
ax_ICa_IKCa.set_ylabel('Current (nA)')
ax_ICa_IKCa.set_ylim(-3,1.1)
ax_ICa_IKCa.set_xlim(t1/ms,t2/ms)

ax_IK.spines['right'].set_visible(False)
ax_IK.spines['top'].set_visible(False)
ax_IK.set_ylabel('Current (nA)')
ax_IK.set_ylim(-.1,6)
ax_IK.set_xlim(t1/ms,t2/ms)

ax_pCa.spines['right'].set_visible(False)
ax_pCa.spines['top'].set_visible(False)
ax_pCa.set_ylabel(r'[Ca$^{2+}$] (M)')
ax_pCa.set_yscale("log")
ax_pCa.set_ylim(1e-8,20e-6)
ax_pCa.set_xlim(t1/ms,t2/ms)
ax_pCa.set_xlabel('Time (ms)')

ax_pCa.plot([t1/ms,t2/ms],[exp(pK_electromotor)*1e-7,exp(pK_electromotor)*1e-7],'k--')
#ax_pCa.plot([t1/ms,t2/ms],[KCa,KCa],'k--') # out of view
ax_pCa.plot([t1/ms,t2/ms],[half_inactivation*1e-6,half_inactivation*1e-6],'k--')

fig.tight_layout()

savefig('fig4_model.png', dpi=300)

show()
