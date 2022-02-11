'''
Calculates spontaneous avoiding response frequency vs. standard deviation of noise
'''
from brian2 import *
from behavior import *
from pylab import *

movie = True

C = paramecium_constants()['C']
N = 200
duration = 120*second

tau_noise = 20*ms

eqs= paramecium_equations() + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+Inoise)/C : volt
dInoise/dt = -Inoise/tau_noise + sigma_noise*xi/tau_noise**.5 : amp
sigma_noise : amp
''')

neuron = NeuronGroup(N, eqs, threshold='velocity<0*meter/second', refractory='velocity<=0*meter/second')
neuron.v = paramecium_constants()['EL']
neuron.sigma_noise = linspace(0, .1, N)*nA

S = SpikeMonitor(neuron)

run(duration, report='text')

counts, _ = histogram(S.i, bins=arange(0,N+1))

plot(neuron.sigma_noise/nA, counts/duration)
xlabel(r'$\sigma$ (nA)')
ylabel('F (Hz)')
show()
