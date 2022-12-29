'''
Figure 5
Activation curve of IKir
'''
from os.path import expanduser
import os
import pandas as pd
from pylab import *
import matplotlib.pyplot as plt
from file_management import *
from os.path import join

width, height = 2, 2

table = pd.read_csv(join(config['root'], 'Ciliated 4 mM KCl', 'tables', 'selection_hyperpolarized.csv'))

fig = figure('Activation curve of IKir', (width, height))

V = linspace(-150,0,100)*1e-3
Vm = dot(ones((len(table),1)),V.reshape((1,100))) # matrix
V_IKir = array(table['V_IKir']).reshape((len(table),1))
k_IKir = array(table['k_IKir']).reshape((len(table),1))

activation_curves = 1/(1+exp((Vm-V_IKir)/k_IKir))**2

mean_activation = activation_curves.mean(axis=0)
sd_activation = activation_curves.std(axis=0)

ax = plt.subplot(111)

# Mean curve
#plot(V/1e-3,mean_activation,'k')
# Typical curve (curve with median parameters)
V_IKir_median = table['V_IKir'].median()
k_IKir_median = table['k_IKir'].median()
plot(V/1e-3,1/(1+exp((V-V_IKir_median)/k_IKir_median))**2,'k')

# Cell shown in A
cell = table[table['name']== '2020-05-12 18.44.35 cell']
V_IKir_cell = cell['V_IKir'].mean()
k_IKir_cell = cell['k_IKir'].mean()
plot(V/1e-3,1/(1+exp((V-V_IKir_cell)/k_IKir_cell))**2,'k--')

# or shaded area
#ax.fill_between(V/1e-3,mean_activation-sd_activation,mean_activation+sd_activation, color='k', alpha=0.2)
#plot(V/1e-3,mean_activation-sd_activation,'k--')
#plot(V/1e-3,mean_activation+sd_activation,'k--')
xlabel('V (mV)')
ylabel('$n_{Kir}^2$')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# Landmarks
# for v in ['EL','EK']:
#     x = table[v].median()/1e-3
#     plot([x,x],[-0.1,1],'k--')
EK = table['EK'].median()/1e-3
EL = table['EL'].median()/1e-3
ax.set_xticks([-100,EK,EL,0])
ax.set_xticklabels(['-100','$E_K$','$E_L$','0'])
ax.set_yticks([0,0.5,1])
ax.set_yticklabels(['0','0.5','1'])


ylim(0,1)

# Functional boxplot: interesting but ugly
#fig = plt.figure()
#ax = fig.add_subplot(111)
#fboxplot(data=activation_curves, xdata=V/1e-3, ax = ax)

tight_layout()

savefig('fig2_activation.png', dpi=300)

show()
