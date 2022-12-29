'''
Figure 11.
Shows snapshots of chemotactic trajectories.
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
duration = 50*second
size = 25*mm
Nframes = 10

### Load frames
reader = imageio.get_reader('gradient.mp4')
frames = [reader.get_data(int(t/dt)) for t in linspace(0*second, duration-dt, Nframes)]
reader.close()

### Add horizontal borders
border = zeros((1, frames[0].shape[1], 3), dtype=int)
frames_and_borders = []
for frame in frames[:-1]:
    frames_and_borders.extend([frame, border])
frames_and_borders.append(frames[-1])
image = vstack(frames_and_borders)

### Figure
fig = figure('Chemotaxis', (width,height))
imshow(image)

h, w = image.shape[:2]

xticks(linspace(0,w,6), linspace(0,size/mm,6))
yticks(linspace(0,h,6), linspace(0,duration/second,6))
xlabel('x (mm)')
ylabel('Time (s)')

fig.tight_layout()

savefig('fig8_chemotaxis.png', dpi=300)

show()
