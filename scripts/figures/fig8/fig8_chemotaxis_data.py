'''
Simulates 200 trajectories in a chemical gradient.
'''
from brian2 import *
from behavior import *
import imageio
from plotting import cell_mask, cell_indices

movie = True

C = paramecium_constants()['C']
N = 200
duration = 50*second
tau_noise = 20*ms
sigma_noise = .009*nA # .09*nA

size = 25000 # in um # observation field
height = 500 # in um
pixel_size = 10 # in um
size_pix = int(size/pixel_size)
height_pix = int(height/pixel_size)

I0 = 1*nA

tau_stim = 50*ms
tau_adapt = 200*ms

x0 = 10*mm

xinit = 5*mm

eqs= paramecium_equations() + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+Inoise-I)/C : volt
dInoise/dt = -Inoise/tau_noise + sigma_noise*xi/tau_noise**.5 : amp
I = I0*(m-h) : amp
dm/dt = (stim-m)/tau_stim : 1 # ON pathway
dh/dt = (stim-h)/tau_adapt : 1 # OFF pathway
stim = x/x0 : 1
x : meter
y : meter
z : meter
orientation : 1
''')

neuron = NeuronGroup(N, eqs, threshold='velocity<0*meter/second', refractory='velocity<=0*meter/second')
neuron.v = paramecium_constants()['EL']
neuron.x = xinit
neuron.y = rand(N)*height*um
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
    cells.set_rotation_angle(neuron.theta_[:], spin=neuron.omega_[:]) # very fast

    cells.x[:,0] = neuron.x_*1e6
    cells.x[:,1] = neuron.y_*1e6
    cells.x[:,2] = neuron.z_*1e6
    cells.integrate()
    x, y, z = cells.x.T

    # Torus topology
    y = y % height
    neuron.x, neuron.y, neuron.z = x*um, y*um, z*um
    neuron.orientation = cells.orientation()

run(duration, report='text')

print('AR frequency:',len(S.i)*1./(N*duration))

x = M.x/um
y = M.y/um
z = M.z/um
t = M.t
orientation = M.orientation

if movie:
    # Movie
    writer = imageio.get_writer('gradient.mp4', fps=30.)
    image = ones((int(height_pix), int(size_pix)))
    for i in range(x.shape[1]):
        print('{}/{}'.format(i,x.shape[1]))
        image[:] = 1
        for k in range(x.shape[0]):
            rr,cc = cell_indices(x[k,i], y[k,i], image, pixel_size=pixel_size, theta=orientation[k,i])
            image[rr,cc] = 0
        writer.append_data((image*255).astype(uint8))

    writer.close()


# Traces
#
# figure()
#
# for i in range(N):
#     plot(x[i,:]*1e-3,t,'k')
# xlabel('x (mm)')
# ylabel('t (s)')
#
# show()
