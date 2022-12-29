'''
IV curves for Fig. 6
(Ciliated cells with 0 and 4 mM KCl)
'''
import pandas as pd
from brian2 import second, volt, amp, ms
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
from file_management import *
from os.path import join, split
import os

width, height = 2,2

overwrite = True

table = pd.read_csv(join(config['root'], 'Deciliated', 'tables', 'selection_deciliated.csv'))

# Temporary files
output_name = 'IV_Fig3.txt'

# Load IV curves
I_coords = linspace(-4,4,100)*1e-9

def load_IV_curves(filenames):
    V_mean = []

    for filename in filenames:
        print(filename)
        data = rename_electrophysiology_data(load_multiple_data(filename,'electrophysiology/data'))
        t, v, I = data['t']/second, data['v']/volt, data['I']/amp
        stimulus_start, stimulus_end = stimulus_time(one_protocol(filename))
        I_late = median(I[:,(t>stimulus_end/second-20*1e-3) & (t<stimulus_end/second)], axis=1)
        V_late = median(v[:,(t>stimulus_end/second-20*1e-3) & (t<stimulus_end/second)], axis=1)
        if I_late[0]>I_late[-1]:
            I_late = I_late[::-1] # I is ordered from high to low
            V_late = V_late[::-1]
        V_mean.append(interp(I_coords, I_late, V_late))

    return array(V_mean)

if (not os.path.exists(output_name)) or overwrite:
    IV = load_IV_curves([join(config['root'], 'Deciliated',name) for name in table['name']])
    np.savetxt(output_name, IV)
else:
    IV = np.loadtxt(output_name)


# Relative to resting potential
# for i in range(IV_4KCl.shape[0]):
#     IV_4KCl[i,:] -= IV_4KCl[i,50]
# for i in range(IV_0KCl.shape[0]):
#     IV_0KCl[i,:] -= IV_0KCl[i,50]

# Figure
fig = figure('IV curve of ciliated cells', (width, height))
ax = plt.subplot(111)
#for i in range(IV.shape[0]):
#    plot(IV[i,:]/1e-3,I_coords/1e-9,'k')
plot(median(IV,axis=0)/1e-3,I_coords/1e-9,'k')
plot([-100,20],[0,0],'k--')
ax.fill_betweenx(I_coords/1e-9,(IV.mean(axis=0)-IV.std(axis=0))/1e-3,(IV.mean(axis=0)+IV.std(axis=0))/1e-3, color='k', alpha=0.2)
#xlabel('$V-V_0$ (mV)')
xlabel('V (mV)')
ylabel('I (nA)')
xlim(-100,40)
#ylim(-4,4)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

tight_layout()

savefig('fig3_IV_curves.png', dpi=300)


show()
