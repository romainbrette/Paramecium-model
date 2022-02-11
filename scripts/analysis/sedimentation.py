'''
Analyzes particle density vs. time in PIV movies.
Selects those with high initial density.
'''
import pandas as pd
from brian2 import *
from scipy.optimize import curve_fit
from os.path import join
from fitting import *
from file_management import *
import yaml
import os
from file_management.file_utils import up_dir
from clampy import *

width, height = 2, 2

table_filename = join(config['root'], 'Ciliated with PIV', 'tables', 'selection_ciliated.csv')
table = pd.read_csv(table_filename)
filenames = [join(config['root'], 'Ciliated with PIV',name) for name in table['name']]

densities = []
for i,filename in enumerate(filenames):
    density = load_multiple_data(filename, 'piv_density/piv_density')['density']
    d = density.mean(axis=-1)
    if d[:20].mean()>0.5:
        print(filename)
        figure()
        plot(d)
        xlabel('Trial')
        ylabel('Particle density')
        ylim(0,1)

show()
