'''
Figure 2
Activation and time constant curve of IKir
'''
import pandas as pd
from pylab import *
#from statsmodels.graphics.functional import fboxplot
import matplotlib.pyplot as plt
from file_management import *
from os.path import join

width, height = 2, 3

table = pd.read_csv(join(config['root'], 'Deciliated', 'tables', 'selection_deciliated.csv'))

fig = figure('Activation curve of IK',  (width, height))

V = linspace(0,80,100)*1e-3
Vm = dot(ones((len(table),1)),V.reshape((1,100))) # matrix


##### ACTIVATION #####
V_IK = array(table['V_IK']).reshape((len(table),1))
k_IK = array(table['k_IK']).reshape((len(table),1))

activation_curves = 1/(1+exp(-(Vm-V_IK)/k_IK))**2

mean_activation = activation_curves.mean(axis=0)
sd_activation = activation_curves.std(axis=0)

ax1 = plt.subplot(211)

# Mean curve
#plot(V/1e-3,mean_activation,'k')
# Typical curve (curve with median parameters)
V_IK_median = table['V_IK'].median()
k_IK_median = table['k_IK'].median()
plot(V/1e-3,1/(1+exp(-(V-V_IK_median)/k_IK_median))**2,'k')

# Cell shown in A
cell = table[table['name']== '2019-08-09 11.20.06 cell']
V_IK_cell = cell['V_IK'].mean()
k_IK_cell = cell['k_IK'].mean()
plot(V/1e-3,1/(1+exp(-(V-V_IK_cell)/k_IK_cell))**2,'k--')

#xlabel('V (mV)')
ylabel('$n_{K}^2$')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)


##### TIME CONSTANT #####
Vtau_IK = array(table['Vtau_IK']).reshape((len(table),1))
ktau_IK = array(table['ktau_IK']).reshape((len(table),1))
b_IK = array(table['b_IK']).reshape((len(table),1))

time_constant_curves = 0.1e-3 + b_IK/(cosh((Vm-Vtau_IK)/ktau_IK))

mean_time_constant = time_constant_curves.mean(axis=0)
sd_time_constant = time_constant_curves.std(axis=0)

ax2 = plt.subplot(212)

# Typical curve (curve with median parameters)
Vtau_IK_median = table['Vtau_IK'].median()
ktau_IK_median = table['ktau_IK'].median()
b_IK_median = table['b_IK'].median()
plot(V/1e-3,(0.1e-3 + b_IK_median/(cosh((V-Vtau_IK_median)/ktau_IK_median)))/1e-3,'k')

# Cell shown in A
Vtau_IK_cell = cell['Vtau_IK'].mean()
ktau_IK_cell = cell['ktau_IK'].mean()
b_IK_cell = cell['b_IK'].mean()
plot(V/1e-3,(0.1e-3 + b_IK_cell/(cosh((V-Vtau_IK_cell)/ktau_IK_cell)))/1e-3,'k--')

xlabel('V (mV)')
ylabel(r'$\tau_{K}$ (ms)')
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.set_ylim(0,5)

tight_layout()

savefig('fig3_activation.png', dpi=300)

show()
