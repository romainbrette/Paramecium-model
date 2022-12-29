'''
Image of an avoiding reaction, with various stimulation intensities
'''
from brian2 import *
from behavior import *
import imageio
from plotting import cell_mask, cell_indices, plot_cell
import matplotlib.pyplot as plt

width,height = 2,2

t1 = 500*ms
x0, y0 = 500, 800 # in um
all_I0 = array([0.3,.5,5])*nA

C = paramecium_constants['C']

cells = PlaneMovingCells(1, theta=pi / 4)
cells.dt = float(1*ms)

eqs= paramecium_equations + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+I)/C : volt
I = I0*((t>t1)*(t<t1+2*ms)) : amp
x : meter
y : meter
orientation : 1
''')

neuron = NeuronGroup(1, eqs)
neuron.v = paramecium_constants['EL']
neuron.orientation = cells.orientation()
M = StateMonitor(neuron, ('x', 'y', 'orientation'), record = True, dt = 1*ms)

@network_operation(dt=1*ms, when='end')
def update_position():
    cells.set_velocity(neuron.velocity_[:] * 1e6)
    cells.set_rotation_angle(neuron.theta_[:], spin=neuron.omega_[:])

    cells.x[:,0] = neuron.x_*1e6
    cells.x[:,1] = neuron.y_*1e6
    cells.integrate()
    x, y, _ = cells.x.T
    neuron.x, neuron.y = x*um, y*um
    neuron.orientation = cells.orientation()

for I0 in all_I0:
    run(1*second)
    t1 += 1*second


fig = figure('Wall', (width,height))

### Trajectory
ax_trajectory = fig.add_subplot(111)

ax_trajectory.plot(M.x[0]/um, M.y[0]/um, 'r')

T0 = 100*ms
for t in T0 + arange(8)*400*ms:
    i = int(t/(1*ms))
    plot_cell(ax_trajectory, M.x[0,i]/um, M.y[0,i]/um, scale=120, theta=M.orientation[0,i], color='k')

ax_trajectory.spines['right'].set_visible(False)
ax_trajectory.spines['top'].set_visible(False)
ax_trajectory.spines['left'].set_visible(False)
ax_trajectory.spines['bottom'].set_visible(False)
ax_trajectory.set_xticks([])
ax_trajectory.set_yticks([])
#ax_trajectory.set_xlabel('x (µm)')
#ax_trajectory.set_xlabel('y (µm)')
ax_trajectory.set_xlim(-300,280)
ax_trajectory.set_ylim(-560,20)

fig.tight_layout()

savefig('fig6_graded_AR.png', dpi=300)

show()
