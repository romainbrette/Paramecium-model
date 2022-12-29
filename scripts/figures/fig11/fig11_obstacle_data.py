'''
Simulates 100 trajectories on a torus with a central obstacle.
Produces a movie and saves trajectories to file, with physiology data for 10 cells.
'''
from brian2 import *
from behavior import *
import imageio
from plotting import cell_mask, cell_indices

C = paramecium_constants()['C']
N = 100
duration = 20*second

tau_noise = 20*ms
sigma_noise = .009*nA #.09*nA

size = 4000 # in um

# Central obstacle
radius = 1000
obstacle = zeros((int(size), int(size)))
cell_area = sum(cell_mask(size/2, size/2, obstacle, pixel_size=1, theta=0))
y, x = mgrid[0:size,0:size]
obstacle[((x-size/2)**2+(y-size/2)**2<radius**2)] = 1

tau_stim = 40*ms
I0 = 5*nA

eqs= paramecium_equations() + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+Inoise+I)/C : volt
dInoise/dt = -Inoise/tau_noise + sigma_noise*xi/tau_noise**.5 : amp
I = I0*m : amp
dm/dt = (stim-m)/tau_stim : 1
stim : 1
x : meter
y : meter
z : meter
orientation : 1
''')

neuron = NeuronGroup(N, eqs, threshold='velocity<0*meter/second', refractory='velocity<=0*meter/second')
neuron.v = paramecium_constants()['EL']
neuron.x = rand(N)*size*um
neuron.y = rand(N)*size*um
M = StateMonitor(neuron, ('x', 'y', 'z', 'orientation'), record = True, dt = 33*ms)
M2 = StateMonitor(neuron, ('v', 'I', 'Cai_cilia'), record = True, dt = .1*ms)
S = SpikeMonitor(neuron)

cells = PlaneMovingCells(N)
cells.dt = float(1 * ms)
cells.set_orientation(rand(N)*2*pi)
neuron.orientation = cells.orientation()

@network_operation(dt=1*ms, when='end')
def update_position():
    cells.set_velocity(neuron.velocity_[:] * 1e6)
    cells.set_rotation_angle(neuron.theta_[:], spin=neuron.omega_[:])

    cells.x[:,0] = neuron.x_*1e6
    cells.x[:,1] = neuron.y_*1e6
    cells.x[:,2] = neuron.z_*1e6
    cells.integrate()
    x, y, z = cells.x.T

    # Torus topology
    x, y = x % size, y % size
    neuron.x, neuron.y, neuron.z = x*um, y*um, z*um
    neuron.orientation = cells.orientation()

    # Stimulus calculation
    for i in range(N):
        d2 = ((x[i]-size/2)**2+(y[i]-size/2)**2)
        if d2>(radius+60)**2: # not on obstacle
            neuron.stim[i] = 0
        elif d2<(radius-60)**2: # fully in obstacle
            neuron.stim[i] = 1
        else:
            rr, cc = cell_indices(x[i], y[i], obstacle, pixel_size=1, theta=neuron.orientation[i])
            stimulus = sum(obstacle[rr, cc]) / cell_area
            neuron.stim[i] = stimulus

run(duration, report='text')

print('AR frequency:',len(S.i)*1./(N*duration))

x = M.x/um
y = M.y/um
z = M.z/um
orientation = M.orientation

# Save data
savez_compressed('obstacle.npz',x=x,y=y,z=z,orientation=orientation, v=M2.v[0:10]/mV, I=M2.I[0:10]/nA, Ca=M2.Cai_cilia[0:10]/molar)

# Movie
background=1-0.1*obstacle
writer = imageio.get_writer('obstacle.mp4', fps=30.)
image = ones((int(size), int(size)))
for i in range(x.shape[1]):
    print(i,'/',x.shape[1])
    image[:] = 1
    for k in range(N):
        rr, cc = cell_indices(x[k, i], y[k, i], image, pixel_size=1, theta=orientation[k, i])
        image[rr, cc] = 0
    writer.append_data((image * background * 255).astype(uint8))

writer.close()
