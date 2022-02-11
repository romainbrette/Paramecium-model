'''
Fig. 8.
Collective behavior.
Simulation of trajectories with breathing paramecia.
'''
from brian2 import *
from behavior import *
import imageio
from plotting import cell_mask, cell_indices

from brian2 import *
from behavior import *
import imageio
from plotting import cell_mask, cell_indices

movie = True

C = paramecium_constants()['C']
N = 500
duration = 200*second

tau_noise = 20*ms
sigma_noise = .009*nA

size = 10000 # in um
pixel_size = 20 # in um
size_pix = int(size/pixel_size)

dx2 = (pixel_size*um)**2
dy2 = (pixel_size*um)**2

D = 2e-9 * meter**2 /second * 5 # approximately the diffusion coefficient of CO2 in water at 25 °C
CO2_rate = .1/second

dt_min = (dx2*dy2)/(dx2+dy2)/(2*D)
print("Minimum time step for diffusion:",dt_min)

# Background CO2 concentration
CO2 = zeros((int(size_pix), int(size_pix)))
y, x = mgrid[0:size_pix,0:size_pix]
y, x = y*pixel_size, x*pixel_size

I0 = 1*nA

tau_stim = 40*ms
tau_adapt = 200*ms

xinit = size/2*um
x0 = 10*mm

eqs= paramecium_equations() + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+Inoise-I)/C : volt
dInoise/dt = -Inoise/tau_noise + sigma_noise*xi/tau_noise**.5 : amp
I = I0*(m-h) : amp
dm/dt = (stim-m)/tau_stim : 1 # ON pathway
dh/dt = (stim-h)/tau_adapt : 1 # OFF pathway
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
neuron.m = xinit/x0 # Resting value
neuron.h = xinit/x0

M = StateMonitor(neuron, ('x', 'y', 'z', 'orientation'), record = True, dt = 33*ms)
S = SpikeMonitor(neuron)

cells = PlaneMovingCells(N)
cells.dt = float(2 * ms)
cells.set_orientation(rand(N)*2*pi)
neuron.orientation = cells.orientation()

@network_operation(dt=2*ms, when='end')
def update_position():
    cells.set_velocity(neuron.velocity_[:] * 1e6)
    cells.set_rotation_angle(neuron.theta_[:], spin=8*np.pi) # very fast

    cells.x[:,0] = neuron.x_*1e6
    cells.x[:,1] = neuron.y_*1e6
    cells.x[:,2] = neuron.z_*1e6
    cells.integrate()
    x, y, z = cells.x.T

    # Torus topology
    x, y = x % size, y % size
    neuron.x, neuron.y, neuron.z = x*um, y*um, z*um
    neuron.orientation = cells.orientation()

    # Stimulation
    neuron.stim = CO2[size_pix-1 - (y/pixel_size).astype(int), (x/pixel_size).astype(int)]

if movie:
    # Movie
    writer = imageio.get_writer('CO2.mp4', fps=30.)
    image = ones((int(size_pix), int(size_pix)))

cycle_length = 5 # number of diffusion time steps per movie frame
cycle = cycle_length-1

@network_operation(dt=33*ms/cycle_length, when='end')
def diffusion():
    global CO2, cycle

    # CO2 production
    x, y, _ = cells.x.T
    x, y = x % size, y % size
    # note that if two cells are exactly at the same place (unlikely), they are counted just once
    CO2[size_pix-1 - (y/pixel_size).astype(int), (x/pixel_size).astype(int)] += CO2_rate*(33*ms)

    CO2 += D * (33*ms)/cycle_length * (
            (roll(CO2, 1, axis = 1) - 2 * CO2 + roll(CO2, -1, axis = 1)) / dx2
            + (roll(CO2, 1, axis = 0) - 2 * CO2 + roll(CO2, -1, axis = 0))/dy2)

    if movie:
        if cycle == 0:
            image[:] = 1
            CO2_image = 1-CO2/CO2.max()
            orientation = neuron.orientation
            for k in range(x.shape[0]):
                rr,cc = cell_indices(x[k], y[k], image, pixel_size=pixel_size, theta=orientation[k])
                image[rr,cc] = 0
            writer.append_data((image*CO2_image*255).astype(uint8))
        cycle = (cycle+1) % cycle_length


run(duration, report='text')

print('AR frequency:',len(S.i)*1./(N*duration))

x = M.x/um
y = M.y/um
z = M.z/um
orientation = M.orientation

if movie:
    writer.close()
