'''
Make fit tables with parameters from fits of all cells.
'''
import sys
from file_management import *
import yaml
import pandas as pd
from brian2 import *
from os.path import join, split
import os

### Command line argument: path
try:
    path = sys.argv[1]
except:
    path = os.path.expanduser('~/hodgkin/Paramecium/Electrophysiology/Selection - AP model/Ciliated with PIV')

table_folder = make_subdir(path, 'tables')

# Dictionary of tables
table = {}

### Go through all cells
for folder in cell_folders(path):
    cell_name = split(folder)[1]
    # Go through all fit files
    for fit in os.scandir(join(folder,'fits')):
        if fit.name[-5:] == '.yaml':
            # Load
            with open(fit.path,'r') as fp:
                description = yaml.load(fp)
            name = description['name']

            # Extract and evaluate constants
            constants = description['model']['constants']
            for x in constants:
                if isinstance(constants[x], str):
                    constants[x] = float(eval(constants[x]))

            # Make row
            row = {'name': cell_name, 'fit_date': description['date']}
            row.update(constants)
            for var, value in description['errors'].items():
                row['error_'+var] = value

            # Add to panda table
            if name not in table:
                table[name] = pd.DataFrame(row, index=[0])
            else:
                table[name] = pd.concat([table[name], pd.DataFrame(row, index=[0])], sort=False, ignore_index=True)

### Save tables
for name in table.keys():
    table[name].to_csv(join(table_folder, name+'.csv'))
    table[name].to_excel(join(table_folder, name+'.xlsx'))
