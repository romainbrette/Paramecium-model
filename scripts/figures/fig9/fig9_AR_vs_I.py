'''
Properties of the graded avoided reaction.
In 2D.

Angle is calculated as average over 1 s (= 1 cycle).
'''
from brian2 import *
from behavior import *
from scipy.linalg import norm
from pylab import *
from scipy.stats import circmean

width, height = 2, 4

t1 = 1000*ms
t2 = 1002*ms

N = 300
halfN = int(N/2)

# Lifting
def lift(x):
    # Returns y such that x = y % (2*pi) and y is continuous.
    x = x % (2*pi)
    cycles = 0*x
    cycles[1:][diff(x)<-pi] = 2*pi # adding one cycle
    cycles[1:][diff(x)>pi] = -2*pi # removing one cycle
    return x+cumsum(cycles)

C = paramecium_constants['C']


eqs= paramecium_equations + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKCa_cilia+I)/C : volt
I = I0*(t>t1)*(t<t2) : amp
I0 : amp
orientation : 1
''')

neuron = NeuronGroup(N, eqs, threshold='velocity>0*meter/second', refractory='velocity>=0*meter/second')
neuron.v = paramecium_constants['EL']
currents = exp(linspace(log(0.01),log(10),halfN))*nA
neuron.I0[:halfN] = currents
neuron.I0[halfN:] = currents
M = StateMonitor(neuron, 'orientation', record = True, dt = 1*ms)
S = SpikeMonitor(neuron) # records the end time of backward swimming

cells = PlaneMovingCells(N, theta=[0*pi/2]*halfN + [-pi/2]*halfN)
cells.dt = float(1 * ms)
neuron.orientation = cells.orientation()

@network_operation(dt=1*ms, when='end')
def update_position():
    cells.set_velocity(neuron.velocity_[:] * 1e6)
    cells.set_rotation_angle(neuron.theta_[:], spin=neuron.omega_[:])
    cells.integrate()
    neuron.orientation = cells.orientation()

run(3*second, report='text')

## Calculate angles
orientation_start = circmean(M.orientation[:,M.t<1*second], axis=1)
orientation_end = circmean(M.orientation[:,M.t>2*second], axis=1)
orientation_end[:halfN] = lift(orientation_end[:halfN])
orientation_end[halfN:] = lift(orientation_end[halfN:])
angle = orientation_end - orientation_start

## Calculate backward swimming duration
duration = zeros(N)*second
for i in range(N):
    spikes = S.spike_trains()[i]
    if len(spikes)>1: # Backward swimming
        duration[i] = spikes[1]-1*second
    else:
        duration[i] = 0*second

# Threshold current
Ith = neuron.I0[(duration>0*second).nonzero()[0][0]]
print('Threshold current:',Ith)

fig = figure('Angle', (width,height))
ax_duration = fig.add_subplot(211)
ax_duration.semilogx(neuron.I0[:halfN]/nA,duration[:halfN]/ms,'k')
ax_duration.set_ylabel('Backward duration (ms)')
#ax_duration.set_xlabel('I (nA)')
ax_duration.semilogx([Ith/nA, Ith/nA], [0,150], 'k--')
ax_duration.set_ylim(0,150)
ax_duration.set_xticks([0.1,1,10])
ax_duration.spines['right'].set_visible(False)
ax_duration.spines['top'].set_visible(False)

ax_angle = fig.add_subplot(212)
ax_angle.semilogx(neuron.I0[:halfN]/nA,angle[:halfN]*180/pi,'k')
ax_angle.semilogx(neuron.I0[halfN:]/nA,angle[halfN:]*180/pi,'r')
ax_angle.semilogx([Ith/nA, Ith/nA], [-120,120], 'k--')
ax_angle.set_ylim(-120,120)
ax_angle.set_xticks([0.1,1,10])
ax_angle.set_xlabel('I (nA)')
ax_angle.set_ylabel('Reorientation (°)')
ax_angle.spines['right'].set_visible(False)
ax_angle.spines['top'].set_visible(False)

tight_layout()

savefig('fig6_AR_vs_I.png', dpi=300)

show()
