'''
Omega (spinning speed) vs. calcium concentration
'''
from pylab import *

width, height = 2, 2

K_electromotor = 1.4e-6 #2.4e-6 # in uM
n_electromotor_coupling = 2

omega_min = 1.
omega_max = 4.

fig = figure('Angle', (width,height))
ax = fig.add_subplot(111)

x = 1e-7*exp(linspace(0,6,100))

#electromotor_coupling = 1/(1+(x/K_electromotor)**n_electromotor_coupling)
#omega1 = omega_min + (omega_max-omega_min)*(1-(2*electromotor_coupling-1)**2)/(1+(2*electromotor_coupling-1)**2)
omega = omega_min + 2*(omega_max-omega_min)/((K_electromotor/x)**2 + (x/K_electromotor)**2)

ax.semilogx(x, omega,'k')
#ax.semilogx(x, omega1,'r')

ax.set_xlim(1e-7,5e-5)
ax.set_ylim(0,4.1)

ax.set_xlabel(r'[Ca$^{2+}$] (M)')
ax.set_ylabel(r'$\omega/(2\pi)$ (Hz)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

tight_layout()

savefig('fig6_omega_calcium.png', dpi=300)

show()
