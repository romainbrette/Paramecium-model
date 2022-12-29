'''
Figure 7
Statistics of ciliated fits
'''
import pandas as pd
from pylab import *
from matplotlib import gridspec
import seaborn
from file_management import *
from os.path import join

width, height = 3, 5

table = pd.read_csv(join(config['root'], 'Ciliated with PIV', 'tables', 'selection_ciliated.csv'))

box_width = 0.5
dot_size = 4

dots = True

fig = figure('Statistics of ciliated fits',  (width, height))

gs = gridspec.GridSpec(4, 2, width_ratios=[1, 1])

print(table['error_v'].describe())
print()

VCa = table['VCa_cilia']/1e-3
print()
print(VCa.describe())
ax4 = fig.add_subplot(gs[0,0])
seaborn.boxplot(y=VCa, color='gray', width=box_width, ax=ax4)
if dots:
    seaborn.swarmplot(y=VCa,  color='0.2', size=dot_size, ax=ax4)
seaborn.despine(bottom=True, ax=ax4)
ax4.set_ylabel(r'$V_{Ca}$ (mV)')
ax4.set_ylim(-20, 20)
ax4.set_xticks([])

kCa = table['kCa_cilia']/1e-3
print()
print(kCa.describe())
ax6 = fig.add_subplot(gs[1, 0])
seaborn.boxplot(y=kCa, color='gray', width=box_width, ax=ax6)
if dots:
    seaborn.swarmplot(y=kCa,  color='0.2', size=dot_size, ax=ax6)
seaborn.despine(bottom=True, ax=ax6)
ax6.set_ylabel(r'$k_{Ca}$ (mV)')
ax6.set_ylim(0, 10)
ax6.set_xticks([])

tau_Ca = table['taum_Ca_cilia']/1e-3
print()
print(tau_Ca.describe())
ax8 = fig.add_subplot(gs[0, 1])
seaborn.boxplot(y=tau_Ca, color='gray', width=box_width, ax=ax8)
if dots:
    seaborn.swarmplot(y=tau_Ca,  color='0.2', size=dot_size, ax=ax8)
seaborn.despine(bottom=True, ax=ax8)
ax8.set_ylabel(r'$\tau_{Ca}$ (ms)')
ax8.set_ylim(0, 5)
ax8.set_xticks([])

nCa = table['nCaM_Ca_cilia']
print()
print(nCa.describe())
ax9 = fig.add_subplot(gs[2, 0])
seaborn.boxplot(y=nCa, color='gray', width=box_width, ax=ax9)
if dots:
    seaborn.swarmplot(y=nCa,  color='0.2', size=dot_size, ax=ax9)
seaborn.despine(bottom=True, ax=ax9)
ax9.set_ylabel(r'$n_{Ca}$')
ax9.set_ylim(0, 8)
ax9.set_xticks([])

nKCa = table['nCaM_KCa_cilia']
print()
print(nKCa.describe())
ax10 = fig.add_subplot(gs[3, 0])
seaborn.boxplot(y=nKCa, color='gray', width=box_width, ax=ax10)
if dots:
    seaborn.swarmplot(y=nKCa,  color='0.2', size=dot_size, ax=ax10)
seaborn.despine(bottom=True, ax=ax10)
ax10.set_ylabel(r'$n_{KCa}$')
ax10.set_ylim(0, 8)
ax10.set_xticks([])

KCa = exp(table['pKCa'])*1e-7 # in uM
print()
print((1e6*KCa).describe())
ax12 = fig.add_subplot(gs[1, 1])
seaborn.boxplot(y=KCa, color='gray', width=box_width, ax=ax12)
if dots:
    seaborn.swarmplot(y=KCa,  color='0.2', size=dot_size, ax=ax12)
seaborn.despine(bottom=True, ax=ax12)
ax12.set_ylabel(r'$K_{Ca}$ (M)')
ax12.set_ylim(1e-7,1e-5)
ax12.set_yscale("log")
ax12.set_xticks([])
print((table['pKCa']/log(10)-7).describe())

KKCa = exp(table['pKKCa'])*1e-7
print()
print((1e6*KKCa).describe())
ax13 = fig.add_subplot(gs[3, 1])
seaborn.boxplot(y=KKCa, color='gray', width=box_width, ax=ax13)
if dots:
    seaborn.swarmplot(y=KKCa,  color='0.2', size=dot_size, ax=ax13)
seaborn.despine(bottom=True, ax=ax13)
ax13.set_ylabel(r'$K_{KCa}$ (M)')
ax13.set_ylim(1e-7, 1e-3)
ax13.set_yscale("log")
ax13.set_xticks([])
print((table['pKKCa']/log(10)-7).describe())

Kelectromotor = exp(table['pK_electromotor'])*1e-7 # in uM
print()
print((1e6*Kelectromotor).describe())
ax14 = fig.add_subplot(gs[2, 1])
seaborn.boxplot(y=Kelectromotor, color='gray', width=box_width, ax=ax14)
if dots:
    seaborn.swarmplot(y=KCa,  color='0.2', size=dot_size, ax=ax14)
seaborn.despine(bottom=True, ax=ax14)
ax14.set_ylabel(r'$K_{motor}$ (M)')
ax14.set_ylim(1e-7,1e-5)
ax14.set_yscale("log")
ax14.set_xticks([])
print((table['pK_electromotor']/log(10)-7).describe())

print()
print(table['C'].describe())
print()
print(table['EL'].describe())
print()
print((table['Jpumpmax_cilia']*.1).describe()) # in uM/s
print()
print(table['V_IK'].describe())
print()
print((1/table['alpha_cilia']).describe())
print()
print(table['b_IK'].describe())
print()
print(table['gCa_cilia'].describe())
print()
print(table['gKCa_cilia'].describe())
print()
print(table['gL'].describe())
print()
print(table['g_IK'].describe())
print()
print(table['k_IK'].describe())
print()
print(table['n_electromotor'].describe())

tight_layout()

savefig('fig4_stats.png', dpi=300)

show()
