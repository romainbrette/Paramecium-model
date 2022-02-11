'''
Statistics of hyperpolarized fits
'''
import pandas as pd
from pylab import *
from matplotlib import gridspec
import seaborn
from file_management import *
from os.path import join

width, height = 6, 3

table = pd.read_csv(join(config['root'], 'Deciliated', 'tables', 'selection_deciliated.csv'))

# Selection

print(len(table))

box_width = 0.5
dot_size = 4

dots = True

fig = figure('Statistics of deciliated fits',  (width, height))

gs = gridspec.GridSpec(2, 3, width_ratios=[1, 1, 1])

print(table['error_v'].describe())
print()

g = table['g_IK']/1e-9 # g is initially in amp
print(g.describe())
ax1 = fig.add_subplot(gs[0, 0])
seaborn.boxplot(y=g, color='gray', width=box_width, ax=ax1)
if dots:
    seaborn.swarmplot(y=g,  color='0.2', size=dot_size, ax=ax1)
seaborn.despine(bottom=True, ax=ax1)
ax1.set_ylabel('$g_{Kd}$ (nS)')
ax1.set_ylim(0, 800)
ax1.set_xticks([])

tau = table['b_IK']/1e-3
print()
print(tau[tau<10].describe()) # Excluding one outlier
ax2 = fig.add_subplot(gs[1, 0])
seaborn.boxplot(y=tau, color='gray', width=box_width, ax=ax2)
if dots:
    seaborn.swarmplot(y=tau,  color='0.2', size=dot_size, ax=ax2)
seaborn.despine(bottom=True, ax=ax2)
ax2.set_ylabel(r'$\tau_{Kd}$ (ms)')
ax2.set_ylim(0, 10)
ax2.set_xticks([])

V = table['V_IK']/1e-3
print()
print(V.describe())
ax3 = fig.add_subplot(gs[0, 1])
seaborn.boxplot(y=V, color='gray', width=box_width, ax=ax3)
if dots:
    seaborn.swarmplot(y=V,  color='0.2', size=dot_size, ax=ax3)
seaborn.despine(bottom=True, ax=ax3)
ax3.set_ylabel(r'$V_{Kd}$ (mV)')
ax3.set_ylim(0, 100)
ax3.set_xticks([])

Vtau = table['Vtau_IK']/1e-3
print()
print(Vtau.describe())
ax4 = fig.add_subplot(gs[0,2])
seaborn.boxplot(y=Vtau, color='gray', width=box_width, ax=ax4)
if dots:
    seaborn.swarmplot(y=Vtau,  color='0.2', size=dot_size, ax=ax4)
seaborn.despine(bottom=True, ax=ax4)
ax4.set_ylabel(r'$V_{\tau}$ (mV)')
ax4.set_ylim(0, 100)
ax4.set_xticks([])

k = table['k_IK']/1e-3
print()
print(k.describe())
ax5 = fig.add_subplot(gs[1, 1])
seaborn.boxplot(y=k, color='gray', width=box_width, ax=ax5)
if dots:
    seaborn.swarmplot(y=k,  color='0.2', size=dot_size, ax=ax5)
seaborn.despine(bottom=True, ax=ax5)
ax5.set_ylabel(r'$k_{Kd}$ (mV)')
ax5.set_ylim(0, 30)
ax5.set_xticks([])

ktau = table['ktau_IK']/1e-3
print()
print(ktau.describe())
ax6 = fig.add_subplot(gs[1, 2])
seaborn.boxplot(y=ktau, color='gray', width=box_width, ax=ax6)
if dots:
    seaborn.swarmplot(y=ktau,  color='0.2', size=dot_size, ax=ax6)
seaborn.despine(bottom=True, ax=ax6)
ax6.set_ylabel(r'$k_{\tau}$ (ms)')
ax6.set_ylim(0, 30)
ax6.set_xticks([])

tight_layout()

savefig('fig3_stats.png', dpi=300)

show()
