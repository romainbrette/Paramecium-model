'''
Figure 7.
First part, Paramecium bumping into a 'wall', modeling as an instantaneously depolarizing stimulus.
'''
from brian2 import *
from pylab import *
import matplotlib.font_manager as fm
from plotting import *
from matplotlib import gridspec
from behavior import *
import imageio
import numpy as np

fontprops = fm.FontProperties(size=18)

width, height = 8, 3

image = zeros((2000, 2000))
video_rows = slice(800,1200)
video_columns = slice(0,1400)

C = paramecium_constants()['C']
x_wall = 1*mm
I0 = 5*nA

cell = PlaneMovingCell((1000, 1000), theta=pi / 2)
cell.dt = float(1*ms)

eqs= paramecium_equations() + Equations('''
dv/dt = (IL+ICa_cilia+IK+IKir+IKCa_cilia+I)/C : volt
I = I0*stim : amp # (x>x_wall) : amp
stim : 1
x : meter
y : meter
orientation : 1
angle : 1
''')

neuron = NeuronGroup(1, eqs)
neuron.v = paramecium_constants()['EL']
neuron.x = 0*mm
neuron.y = 1*mm
M = StateMonitor(neuron, ('x', 'y', 'orientation', 'angle', 'v', 'I', 'Cai_cilia', 'velocity', 'theta', 'stim'), record = True, dt = .1*ms)

@network_operation(dt=1*ms)
def update_position():
    cell.set_velocity(1e6*float(neuron.velocity[0]))
    cell.set_rotation_angle(float(neuron.theta[0]), spin=neuron.omega[0])
    cell.x = array([neuron.x[0]/um, neuron.y[0]/um,0.])
    axis = cell.spiral_axis()[:2]
    neuron.angle = np.arctan2(axis[1], axis[0])

    cell.integrate()
    x, y, _ = cell.x
    neuron.x[0], neuron.y[0] = x*um, y*um
    neuron.orientation[0] = cell.orientation()

    # Stimulus calculation
    if x<x_wall/um-60: # not on obstacle
        neuron.stim[0] = 0
    elif x>x_wall/um+60: # fully in obstacle
        neuron.stim[0] = 1
    else:
        rr, cc = cell_indices(x, y, image, pixel_size=1, theta=neuron.orientation[0])
        if len(cc)>0:
            stimulus = sum(1*cc>x_wall/um) / len(cc)
            neuron.stim[0] = stimulus

run(4*second)

x, y = M.x[0]/um, M.y[0]/um
theta = M.theta[0]
orientation = M.orientation[0]
cell_angle = M.angle[0]
t = M.t

### Detect contact
i_contact = (M.stim[0]>0).nonzero()[0][0]
t_contact = t[i_contact]
t_end = t_contact+300*ms
i_contact_end = i_contact + (M.stim[0][i_contact:]==0).nonzero()[0][0]
t_contact_end = t[i_contact_end]
print(t_contact, t_contact_end)

### Write movie

writer = imageio.get_writer('fig7_wall.mp4', fps=100.)

for i in range(0,len(x),100):
    im = 0*image
    # The wall
    im[:, int(x_wall/um):] = .5
    rr,cc = cell_indices(x[i], y[i], image, pixel_size=1., theta=orientation[i])
    im[rr, cc] = 1
    if sum(im[video_rows, video_columns]==1)==0: # out of field
        break
    writer.append_data(1-im[video_rows, video_columns])

writer.close()

### Time shift

t = t-t_contact
t_end = t_end-t_contact
t_contact_end = t_contact_end-t_contact
t_contact = 0*second
print("Contact:",t_contact,'to', t_contact_end)


#### FIGURE
gs = gridspec.GridSpec(3, 8)
fig = figure('Wall', (width,height))

### Trajectory
ax_trajectory = fig.add_subplot(gs[0:3,0:3])
ax_trajectory.plot(x,y,'k')
#ax_trajectory.plot([x_wall/um, x_wall/um], (500,1400), 'k--') # wall
ax_trajectory.fill_betweenx(y=(500,1400), x1=x_wall/um, x2=1400, color='k', alpha=0.1)


# Plot cell
i0 = (x>600).nonzero()[0][0]
plot_cell(ax_trajectory, x[i0], y[i0], scale=120, theta=orientation[i0], color='k')
try:
    i1 = ((y<600) | (y>1300)).nonzero()[0][0]
except:
    i1 = len(x)-1 # last frame
plot_cell(ax_trajectory, x[i1], y[i1], scale=120, theta=orientation[i1], color='k')

ax_trajectory.set_xlim(500, 1400)
ax_trajectory.set_ylim(500, 1400)
ax_trajectory.spines['right'].set_visible(False)
ax_trajectory.spines['top'].set_visible(False)
ax_trajectory.spines['left'].set_visible(False)
ax_trajectory.set_yticks([])
ax_trajectory.set_xlabel('x (µm)')
ax_trajectory.set_xticks([600,800,1000,1200,1400])
ax_trajectory.set_xticklabels(['-400','-200','0','200','400'])

### Traces
backward = M.velocity[0]<0
t_BS = t[backward.nonzero()[0][0]]
t_FS_again = t[(diff(backward*1)<0).nonzero()[0][0]]
ind_BS = (t>=t_BS) & (t<t_FS_again)
print("Backward swimming:",t_BS,"to", t_FS_again)

ax1 = fig.add_subplot(gs[0,3:8])
ax1.plot(t/ms, M.v[0]/mV, 'k')
ax1.plot(t[ind_BS]/ms, M.v[0][ind_BS]/mV, 'darkorange')
ax1.set_xlim((t_contact-50*ms)/ms, t_end/ms)
ax1.set_ylim(-25,-5)
ax1.set_ylabel('V (mV)')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
#ax1.spines['bottom'].set_visible(False)
ax1.set_xticklabels([])

ax2 = fig.add_subplot(gs[1,3:8])
ax2.plot(t/ms, M.I[0]/nA, 'k')
ax2.plot(t[ind_BS]/ms, M.I[0][ind_BS]/nA, 'darkorange')
ax2.set_xlim((t_contact-50*ms)/ms, t_end/ms)
ax2.set_ylim(0,0.3)
ax2.set_ylabel('I (nA)')
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
#ax2.spines['bottom'].set_visible(False)
ax2.set_xticklabels([])

ax3 = fig.add_subplot(gs[2,3:8])
ax3.semilogy(t/ms, M.Cai_cilia[0]/molar, 'k')
ax3.semilogy(t[ind_BS]/ms, M.Cai_cilia[0][ind_BS]/molar, 'darkorange')
ax3.set_xlim((t_contact-50*ms)/ms, t_end/ms)
ax3.set_ylim(1e-8,1e-5)
ax3.set_ylabel(r'[Ca$^{2+}$] (M)')
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_xlabel('Time (ms)')

# Object contact
ax1.fill_betweenx(y=ax1.get_ylim(), x1=t_contact/ms, x2=t_contact_end/ms, color='k', alpha=0.1)
ax2.fill_betweenx(y=ax2.get_ylim(), x1=t_contact/ms, x2=t_contact_end/ms, color='k', alpha=0.1)
ax3.fill_betweenx(y=ax3.get_ylim(), x1=t_contact/ms, x2=t_contact_end/ms, color='k', alpha=0.1)


fig.tight_layout()

savefig('fig7_wall.png', dpi=300)

show()
