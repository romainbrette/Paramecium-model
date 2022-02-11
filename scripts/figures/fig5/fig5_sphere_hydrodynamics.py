'''
Fig. 5.
Calculation of motion vectors with asynchronous ciliary reversal.
'''
from hydrodynamics import *
import numpy as np
from pylab import *
import matplotlib.font_manager as fm
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as mpatches

fontprops = fm.FontProperties(size=18)
width, height = 8, 2.5

t = np.linspace(0,4,1000)
v = zeros_like(t)
theta = zeros_like(t)
omega = zeros_like(t)

#### Calculations

# Forward movement
U, Omega = sphere_total_force_torque(np.pi+np.pi/18, np.pi+np.pi/18, np.pi+np.pi/18, np.pi+np.pi/18) # 10°; note that this is the angle of the fluid force, i.e. of swimming or opposite of fluid movement

# Normalization factor to get 500 um/s
factor = .5/translational_velocity(U)
U, Omega = U*factor, Omega*factor

print('Forward swimming')
print('Velocity (mm/s):', translational_velocity(U))
print('Angle of rotation axis (°):',rotation_angle(Omega) * 180/np.pi)
print('Spinning velocity (Hz):',spinning_velocity(Omega))
print('Velocity along spiral axis (mm/s):', speed_along_axis(U, Omega))
print()

v[(t<1) | (t>=3)] = speed_along_axis(U, Omega)
theta[(t<1) | (t>=3)] = rotation_angle(Omega) * 180/np.pi
omega[(t<1) | (t>=3)] = spinning_velocity(Omega)

# Backward movement
U, Omega = sphere_total_force_torque(np.pi+np.pi*17/18, np.pi+np.pi*17/18, np.pi+np.pi*17/18, np.pi+np.pi*17/18) # 10°
U, Omega = U*factor, Omega*factor

print('Backward swimming')
print('Velocity (mm/s):', translational_velocity(U))
print('Angle of rotation axis (°):',rotation_angle(Omega) * 180/np.pi)
print('Spinning velocity (Hz):',spinning_velocity(Omega))
print('Velocity along spiral axis (mm/s):', speed_along_axis(U, Omega))
print()

v[(t>=1) & (t<2)] = -speed_along_axis(U, Omega)
theta[(t>=1) & (t<2)] = rotation_angle(Omega) * 180/np.pi
omega[(t>=1) & (t<2)] = spinning_velocity(Omega)

# Turning
U, Omega = sphere_total_force_torque(np.pi+np.pi/18, np.pi+np.pi*17/18, np.pi+np.pi/2, np.pi+np.pi/2)
U, Omega = U*factor, Omega*factor

print('Turning')
print('Velocity (mm/s):', translational_velocity(U))
print('Angle of rotation axis (°):',rotation_angle(Omega) * 180/np.pi)
print('Spinning velocity (Hz):',spinning_velocity(Omega))
print('Velocity along spiral axis (mm/s):', speed_along_axis(U, Omega))
print()

v[(t>=2) & (t<3)] = speed_along_axis(U, Omega)
theta[(t>=2) & (t<3)] = rotation_angle(Omega) * 180/np.pi
omega[(t>=2) & (t<3)] = spinning_velocity(Omega)

#### Figure

gs = gridspec.GridSpec(3, 4)
fig = figure('Sphere hydrodynamics', (width,height))

# Force fields
# ax_spheres = fig.add_subplot(gs[0,:])
# ax_spheres.add_patch(mpatches.Circle((0.5,0.5), .3))
# dx = .1*sin(np.pi/9)
# dy = -.1*cos(np.pi/9)
# ax_spheres.add_patch(mpatches.FancyArrow(0.5,0.5,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
# ax_spheres.add_patch(mpatches.Circle((3.5,0.5), .3))
# ax_spheres.add_patch(mpatches.FancyArrow(3.5,0.5,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
# ax_spheres.text(0.5,0.9,'Low [Ca]', ha='center')
# ax_spheres.text(1.5,0.9,'High [Ca]', ha='center')
# ax_spheres.text(2.5,0.9,'Medium [Ca]', ha='center')
# ax_spheres.text(3.5,0.9,'Low [Ca]', ha='center')
#
# dx = .1*sin(np.pi*8/9)
# dy = -.1*cos(np.pi*8/9)
# ax_spheres.add_patch(mpatches.Circle((1.5,0.5), .3))
# ax_spheres.add_patch(mpatches.FancyArrow(1.5,0.5,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
#
# ax_spheres.add_patch(mpatches.Circle((2.5,0.5), .3))
# ax_spheres.plot([2.2,2.8],[0.5,0.5],'k')
# ax_spheres.plot([2.5,2.5],[0.5,0.8],'k')
# dx = .1*sin(np.pi/9)
# dy = -.1*cos(np.pi/9)
# ax_spheres.add_patch(mpatches.FancyArrow(2.3,0.65,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
# dx = .1*sin(np.pi*8/9)
# dy = -.1*cos(np.pi*8/9)
# ax_spheres.add_patch(mpatches.FancyArrow(2.62,0.52,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
# dx = .1*sin(np.pi/2)
# dy = -.1*cos(np.pi/2)
# ax_spheres.add_patch(mpatches.FancyArrow(2.45,0.35,dx,dy, head_width=0.05, head_length=0.05, lw=1, color='k'))
#
# ax_spheres.set_xlim(0,4)
# ax_spheres.set_ylim(0,1)
# ax_spheres.spines['right'].set_visible(False)
# ax_spheres.spines['top'].set_visible(False)
# ax_spheres.spines['bottom'].set_visible(False)
# ax_spheres.spines['left'].set_visible(False)
# ax_spheres.set_xticks([])
# ax_spheres.set_yticks([])

# Traces

ax_v = fig.add_subplot(gs[0,:])
ax_v.plot(t, v, 'k')
ax_v.plot(t, 0*t, 'k--')
ax_v.spines['right'].set_visible(False)
ax_v.spines['top'].set_visible(False)
ax_v.spines['bottom'].set_visible(False)
ax_v.set_xticks([])
ax_v.set_ylim(-0.6,0.6)
ax_v.set_ylabel('v (mm/s)')

ax_theta = fig.add_subplot(gs[1,:])
ax_theta.plot(t, theta, 'k')
ax_theta.spines['right'].set_visible(False)
ax_theta.spines['top'].set_visible(False)
ax_theta.spines['bottom'].set_visible(False)
ax_theta.set_xticks([])
ax_theta.set_ylim(-1,40)
ax_theta.set_ylabel(r'$\theta$ (°)')
ax_theta.set_yticks([0,20,40])

ax_omega = fig.add_subplot(gs[2,:])
ax_omega.plot(t, omega, 'k')
ax_omega.spines['right'].set_visible(False)
ax_omega.spines['top'].set_visible(False)
#ax_omega.spines['bottom'].set_visible(False)
ax_omega.set_xticks([])
ax_omega.set_ylim(0,10)
ax_omega.set_ylabel(r'$\omega/(2\pi)$ (Hz)')
ax_omega.set_yticks([0,5,10])

fig.tight_layout()

savefig('fig5_sphere_hydrodynamics.png', dpi=300)

show()
