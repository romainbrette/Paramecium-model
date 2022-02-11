'''
Velocity vs. calcium concentration
'''
from pylab import *

width, height = 2, 2

K_electromotor = 1.4e-6 #2.4e-6 #.5e-6 # in uM
n_electromotor_coupling = 2 # 3.7
v_plus = .5
#v_plus = .55
#el0 = 1/(1+(1e-7/K_electromotor))
#v_plus = .5/(2*el0-1)
#print('v_plus =',v_plus)
v_minus = -v_plus

fig = figure('Angle', (width,height))
ax = fig.add_subplot(111)

x = 1e-7*exp(linspace(0,6,100))

electromotor_coupling = 1/(1+(x/K_electromotor)**n_electromotor_coupling)
v = v_minus + (v_plus-v_minus)*electromotor_coupling

ax.semilogx(x, v,'k')
ax.plot(x,0*x,'k--')

ax.set_xlim(1e-7,5e-5)
ax.set_ylim(-0.6, 0.6)

ax.set_xlabel(r'[Ca$^{2+}$] (M)')
ax.set_ylabel(r'v (mm/s)')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

tight_layout()

savefig('fig6_v_calcium.png', dpi=300)

show()
