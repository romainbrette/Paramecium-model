'''
Fig. 8.
Collective behavior.
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
dt = 33*ms
duration = 200*second
size = 10*mm
Nframes = 4

### Load frames
reader = imageio.get_reader('CO2.mp4')
frames = [reader.get_data(int(t/dt)) for t in [1*second, 30*second, 60*second, 200*second]]
reader.close()

### Add vertical borders
border = zeros((frames[0].shape[0], 1, 3), dtype=int)
frames_and_borders = []
for frame in frames[:-1]:
    frames_and_borders.extend([frame, border])
frames_and_borders.append(frames[-1])
image = hstack(frames_and_borders)

### Figure
fig = figure('Collective behavior', (width,height))

imshow(image)
h, w = image.shape[:2]

#xticks(linspace(0,w,6), linspace(0,size/mm,6))
xticks([])
yticks(linspace(0,h,6), linspace(0,size/mm,6)[::-1])
#xlabel('x (mm)')
ylabel('y (mm)')

fig.tight_layout()

savefig('fig8_CO2.png', dpi=300)

show()
