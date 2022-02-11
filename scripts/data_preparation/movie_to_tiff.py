'''
Splits an mp4 movie, or all mp4 movie in a folder, into tiff files.
Runs in parallel for multiple files.
'''
import imageio
import sys
import os
from file_management.batch_processing import *
from file_management.configuration import *

### Command line argument: path
try:
    path = sys.argv[1]
except:
    path = '/Volumes/didisque/2020-10-28 17.46.05 cell/2020-10-28 17.56.58 normal pulses/images'

# File list
if path[-4:]=='.mp4':
    folder = os.path.splitext(path)[0]
    if not os.path.exists(folder):
        os.mkdir(folder)
    reader = imageio.get_reader(path)
    for i, im in enumerate(reader):
        imageio.imwrite(os.path.join(folder,'{:03d}.tiff'.format(i)), im)
    reader.close()
else: # assuming it's a folder
    files = [f.path for f in os.scandir(path) if f.name[-4:] == '.mp4' and not f.name[0]=='.']
    python = python_binary()  # I suppose it could be obtained otherwise
    print(files)
    cluster_batch(python_binary(), os.path.realpath(__file__), files)
