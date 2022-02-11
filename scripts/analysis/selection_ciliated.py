'''
Selection of ciliated cells with PIV (for Fig. 4).
Discards cell with abnormal passive properties.
'''
import pandas as pd
from file_management.configuration import *
from os.path import join
from numpy import exp

table_folder = join(config['root'],'Ciliated with PIV', 'tables')

# Make the panda table
df = pd.read_csv(join(table_folder,'ciliated.csv'))

# Convert g_IKir to siemens (originally amp)
df['g_IK'] = df['g_IK']/0.0252487776994807 # RT/F

# Calculation of Ki (mM)
df['Ki'] = 4*exp(-df['EK']/0.0252487776994807)

# Sort by date
df = df.sort_values(by=['name'])

n_all_cells = len(df)

# Remove those with unrealistic passive parameters
try:
    df_selected = df[(df['C']<499e-12)
            & (df['gL'] > 2.1e-9) & (df['gL'] < 33e-9)  # 30 to 500 MOhm
            & (df['EL']>df['EK']) ]
except KeyError:
    pass

print('{}/{} cells'.format(len(df_selected),len(df)))

df_selected.to_csv(join(table_folder,'selection_ciliated.csv'))
df_selected.to_excel(join(table_folder,'selection_ciliated.xlsx'))
