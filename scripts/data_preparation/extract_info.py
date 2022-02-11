'''
Extract information from cell folders
'''
from file_management.batch_processing import *
from file_management.configuration import *
import sys
from os.path import join, split
import yaml
import pandas as pd
import datetime

# Parse command line arguments
args = sys.argv
try:
    path = args[1]
except:
    path = '/Volumes/didisque/Selection - AP model/Deciliated'

folders = cell_folders(path, recursive=False)

table = {}

for folder in sorted(folders):
    cell_name = split(folder)[1]
    print(cell_name)
    with open(join(folder, 'notes.yaml'), 'r') as fp:
        description = yaml.load(fp)
    KCl = description['electrodes']['solution'].get('KCl', 1)
    particles = description.get('particles','None')
    colchicine = 'colchicine' in description['solution']
    date = description['date']
    print(date, KCl, particles, colchicine)

    # Add to panda table
    row = {'date' : date, 'KCl' : KCl, "particles" : particles, "colchicine" : colchicine}
    if len(table) == 0:
        table = pd.DataFrame(row, index=[0])
    else:
        table = pd.concat([table, pd.DataFrame(row, index=[0])], sort=False, ignore_index=True)

table.to_excel(join(path, 'info.xlsx'))
