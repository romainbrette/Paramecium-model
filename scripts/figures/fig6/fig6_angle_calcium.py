'''
Angle vs. calcium concentration
'''
from pylab import *

width, height = 2, 2

K_electromotor = 1.4e-6 #2.4e-6 # in uM
n_electromotor_coupling = 2

theta_min = 13.
theta_max = 90.

fig = figure('Angle', (width,height))
ax = fig.add_subplot(111)

x = 1e-7*exp(linspace(0,6,100))

theta = theta_min + 2*(theta_max-theta_min)/((K_electromotor/x)**2 + (x/K_electromotor)**2)

ax.semilogx(x, theta,'k')
#ax.semilogx(x, theta1,'r')

ax.set_xlim(1e-7,5e-5)
ax.set_ylim(0,100)

ax.set_xlabel(r'[Ca$^{2+}$] (M)')
ax.set_ylabel(r'$\theta$ (°)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

tight_layout()

savefig('fig6_angle_calcium.png', dpi=300)

show()
