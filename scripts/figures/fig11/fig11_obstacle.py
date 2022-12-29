'''
Figure 11.
Trajectories with an obstacle and torus topology.
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

width, height = 4, 8

t_start = 0*second
t_end = 20*second

size = 4000 # in um
radius = 1000

### Load data
i0 = 1 # We select one cell
dt = 33*ms
data = load('obstacle.npz')
x, y = data['x'], data['y']
v, I, Ca = data['v'][i0], data['I'][i0], data['Ca'][i0]
t = arange(x.shape[1])*dt
N = x.shape[0]
print(N,'cells')

### Proportion of cells inside the object
proportion_in = ((((x-size/2)**2 + (y-size/2)**2)<radius**2)*1.).mean(axis=0)
print('Initial proportion of cells in disk:',proportion_in[0],'%')

# Select the second half
#x = x[:,int(t_start/dt):int(t_end/dt)]/1000.
#y = y[:,int(t_start/dt):int(t_end/dt)]/1000.
x = x/1000.
y = y/1000.

### Figure

fig = figure('Obstacle', (width,height))
gs = gridspec.GridSpec(8, 4)

# Plot trajectories with care to torus crossings
ax_trajectories = fig.add_subplot(gs[0:4,:])
for i in range(N):
    crossings = list(((diff(vstack([x[i],y[i]]), axis=1)**2).sum(axis=0)>1e-1).nonzero()[0])
    crossings.append(x.shape[1])
    previous = -1
    for k in crossings:
        ax_trajectories.plot(x[i,previous+1:k], y[i,previous+1:k],'k')
        previous = k

# Selection of part of trajectory i0
x, y = x[i0,int(t_start/dt):], y[i0,int(t_start/dt):]
crossings = list(((diff(vstack([x, y]), axis=1) ** 2).sum(axis=0) > 1e-1).nonzero()[0])
crossings.append(len(x))
previous = -1
for k in crossings:
    ax_trajectories.plot(x[previous + 1:k], y[previous + 1:k], 'r')
    previous = k

ax_trajectories.spines['right'].set_visible(False)
ax_trajectories.spines['top'].set_visible(False)
ax_trajectories.set_xlabel("x (mm)")
ax_trajectories.set_ylabel("y (mm)")

# Proportion inside the object
ax0 = fig.add_subplot(gs[4,:])
ax0.plot(t/second, 100*proportion_in, 'k')
ax0.set_ylabel('Cells in disk (%)')
ax0.spines['right'].set_visible(False)
ax0.spines['top'].set_visible(False)
#ax0.set_xticklabels([])
ax0.set_ylim(0,25)

# Traces
print(t_start, t_end)
dt = 0.1*ms
t = arange(len(v))*dt
ax1 = fig.add_subplot(gs[5,:])
ax1.plot(t/second, v, 'k')
ax1.set_xlim(t_start/second, t_end/second)
#ax1.set_ylim(-28,-18)
ax1.set_ylabel('V (mV)')
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
#ax1.spines['bottom'].set_visible(False)
#ax1.set_xticklabels([])

ax2 = fig.add_subplot(gs[6,:])
ax2.plot(t/second, I, 'k')
ax2.set_xlim(t_start/second, t_end/second)
#ax2.set_ylim(0,0.3)
ax2.set_ylabel('I (nA)')
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
#ax2.spines['bottom'].set_visible(False)
#ax2.set_xticklabels([])

ax3 = fig.add_subplot(gs[7,:])
ax3.semilogy(t/second, Ca, 'k')
ax3.set_xlim(t_start/second, t_end/second)
ax3.set_ylim(1e-8,1e-5)
ax3.set_ylabel(r'[Ca$^{2+}$] (M)')
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.set_xlabel('Time (s)')


fig.tight_layout()

savefig('fig8_obstacle.png', dpi=300)

show()
