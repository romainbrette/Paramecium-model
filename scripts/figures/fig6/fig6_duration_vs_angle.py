'''
Observed relation between backward swimming duration and reorientation angle
'''
from pylab import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from scipy.stats import linregress
import scipy.stats as st

duration, angle = loadtxt('DurationBS_CumulatedRotAngle_Phi0_20201016.txt').T
x, y = (duration+.02*(rand(len(duration))-.5))*1000, angle

print('Duration = ',mean(x),'+-',std(x),'; median',median(x))
print('Angle = ',mean(y),'+-',std(y),'; median',median(y))

print('Linear regression:')
slope, intercept, r, p, _ = linregress(x, y)
print('r =', r)
print('p =', p)

fig = figure(figsize=(4, 4))
gs = gridspec.GridSpec(4, 4)
ax_main = fig.add_subplot(gs[1:4, :3])
ax_xDist = fig.add_subplot(gs[0, :3], sharex=ax_main)
ax_yDist = fig.add_subplot(gs[1:4, 3], sharey=ax_main)

# Perform the kernel density estimate
xmin, xmax = 0, 300
ymin, ymax = 0, 180
xx, yy = np.mgrid[xmin:xmax:100j, ymin:ymax:100j]
positions = np.vstack([xx.ravel(), yy.ravel()])
values = np.vstack([x, y])
kernel = st.gaussian_kde(values)
f = np.reshape(kernel(positions).T, xx.shape)
cfset = ax_main.contourf(xx, yy, f, cmap='Blues')

print('Proportion of points outside view:', 100*mean(1.*((x>xmax) | (y>ymax))), '%')

ax_main.scatter(x, y, color='k', marker='.', s=1)
#x_regression = np.array([0, 500])
#ax_main.plot(x_regression, intercept + slope*x_regression, 'k--')
ax_main.set(xlabel="Duration (ms)", ylabel="Angle (°)")
ax_main.set_xlim(xmin, xmax)
ax_main.set_ylim(ymin, ymax)
ax_main.set_yticks([0,90,180])

ax_xDist.hist(x, bins=50, color='k', align='mid')
ax_xDist.set_axis_off()

ax_yDist.hist(y, bins=50, color='k', orientation='horizontal', align='mid')
ax_yDist.set_axis_off()

fig.tight_layout()

savefig('fig6_duration_vs_angle.png', dpi=300)

show()
