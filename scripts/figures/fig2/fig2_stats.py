'''
Statistics of hyperpolarized fits
'''
import pandas as pd
from pylab import *
from matplotlib import gridspec
import seaborn
from file_management import *
from os.path import join

width, height = 8, 3

table = pd.read_csv(join(config['root'], 'Ciliated 4 mM KCl', 'tables', 'selection_hyperpolarized.csv'))

# Selection

print(len(table))

box_width = 0.5
dot_size = 4

dots = True

fig = figure('Statistics of hyperpolarized fits', (width, height))

gs = gridspec.GridSpec(2, 4, width_ratios=[1, 1, 1, 1])

C = table['C']/1e-12 # in pF
print(C.describe())
ax1 = fig.add_subplot(gs[0, 0])
seaborn.boxplot(y=C, color='gray', width=box_width, ax=ax1)
if dots:
    seaborn.swarmplot(y=C,  color='0.2', size=dot_size, ax=ax1)
seaborn.despine(bottom=True, ax=ax1)
ax1.set_ylabel('$C$ (pF)')
ax1.set_ylim(0, 500)
ax1.set_xticks([])

#R = (1/table['gL'])/1e6
R = table['Rtot']/1e6
print()
print(R.describe())
ax2 = fig.add_subplot(gs[1, 0])
seaborn.boxplot(y=R, color='gray', width=box_width, ax=ax2)
if dots:
    seaborn.swarmplot(y=R,  color='0.2', size=dot_size, ax=ax2)
seaborn.despine(bottom=True, ax=ax2)
ax2.set_ylabel(r'$R$ (M$\Omega$)')
ax2.set_ylim(0, 300)
ax2.set_xticks([])

print()
print(table['g(EL)/(g(EL)+gL)'].describe())

#EL = table['EL']/1e-3
V0 = table['V0']/1e-3
print()
print(V0.describe())
ax3 = fig.add_subplot(gs[0, 1])
seaborn.boxplot(y=V0, color='gray', width=box_width, ax=ax3)
if dots:
    seaborn.swarmplot(y=V0,  color='0.2', size=dot_size, ax=ax3)
seaborn.despine(bottom=True, ax=ax3)
ax3.set_ylabel('$V_0$ (mV)')
ax3.set_ylim(-80, 0)
ax3.set_xticks([])

EK = table['EK']/1e-3
print()
print(EK.describe())
print()
print(table['Ki'].describe())
ax8 = fig.add_subplot(gs[1, 1])
seaborn.boxplot(y=EK, color='gray', width=box_width, ax=ax8)
if dots:
    seaborn.swarmplot(y=EK,  color='0.2', size=dot_size, ax=ax8)
seaborn.despine(bottom=True, ax=ax8)
ax8.set_ylabel('$E_K$ (mV)')
ax8.set_ylim(-80,0)
ax8.set_xticks([])

VKir = table['V_IKir']/1e-3
print()
print(VKir.describe())
ax4 = fig.add_subplot(gs[0, 3])
seaborn.boxplot(y=VKir, color='gray', width=box_width, ax=ax4)
if dots:
    seaborn.swarmplot(y=VKir,  color='0.2', size=dot_size, ax=ax4)
seaborn.despine(bottom=True, ax=ax4)
ax4.set_ylabel('$V_{Kir}$ (mV)')
ax4.set_ylim(-205, 0)
ax4.set_xticks([])

g = table['g_IKir']/1e-9
print()
print(g.describe())
ax5 = fig.add_subplot(gs[0, 2])
seaborn.boxplot(y=g, color='gray', width=box_width, ax=ax5)
if dots:
    seaborn.swarmplot(y=g,  color='0.2', size=dot_size, ax=ax5)
seaborn.despine(bottom=True, ax=ax5)
ax5.set_ylabel('$g_{Kir}$ (nS)')
ax5.set_ylim(0, 4000)
ax5.set_xticks([])

k = table['k_IKir']/1e-3
print()
print(k.describe())
ax6 = fig.add_subplot(gs[1, 2])
seaborn.boxplot(y=k, color='gray', width=box_width, ax=ax6)
if dots:
    seaborn.swarmplot(y=k,  color='0.2', size=dot_size, ax=ax6)
seaborn.despine(bottom=True, ax=ax6)
ax6.set_ylabel('$k_{Kir}$ (mV)')
ax6.set_ylim(0, 60)
ax6.set_xticks([])

tau = table['tau_IKir']/1e-3
print()
print(tau.describe())
ax7 = fig.add_subplot(gs[1, 3])
seaborn.boxplot(y=tau, color='gray', width=box_width, ax=ax7)
if dots:
    seaborn.swarmplot(y=tau,  color='0.2', size=dot_size, ax=ax7)
seaborn.despine(bottom=True, ax=ax7)
ax7.set_ylabel(r'$\tau_{Kir}$ (ms)')
ax7.set_ylim(0, 30)
ax7.set_xticks([])

tight_layout()

savefig('fig2_stats.png', dpi=300)

show()
