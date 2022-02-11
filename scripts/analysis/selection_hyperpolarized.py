'''
Selection of hyperpolarized cells (for Fig. 2).
Discards cell with abnormal passive properties.
'''
import pandas as pd
from file_management.configuration import *
from os.path import join
from numpy import exp

for concentration in ['0', '4']:
    table_folder = join(config['root'],'Ciliated '+concentration+' mM KCl', 'tables')

    # Make the panda table
    df = pd.read_csv(join(table_folder,'hyperpolarized.csv'))

    # Convert g_IKir to siemens (originally amp)
    df['g_IKir'] = df['g_IKir']/0.0252487776994807 # RT/F

    # Calculations of effective resistance and resting potential
    df['g(EL)'] = df['g_IKir']*exp(2*(df['V_IKir']-df['EL'])/df['k_IKir'])
    df['g(EL)/(g(EL)+gL)'] = df['g(EL)']/(df['g(EL)']+df['gL'])
    df['Rtot'] = 1/(df['gL']+df['g(EL)'])
    df['V0'] = (df['gL']*df['EL']+df['g(EL)']*df['EK'])/(df['gL']+df['g(EL)'])

    # Calculation of Ki (mM)
    df['Ki'] = int(concentration)*exp(-df['EK']/0.0252487776994807)

    # Sort by date
    df = df.sort_values(by=['name'])

    n_all_cells = len(df)

    # Remove those with unrealistic passive parameters
    selection = ((df['C']<499e-12) &
                  (df['Rtot']>30e6) & (df['Rtot']<500e6) # 30 to 500 MOhm # this might not be very important
                & (df['EK']<df['V0']))
    df_selected = df[selection]
    df_unselected = df[~selection]

    print('{} mM KCl : {}/{} cells'.format(concentration,len(df_selected),len(df)))

    df_selected.to_csv(join(table_folder,'selection_hyperpolarized.csv'))
    df_selected.to_excel(join(table_folder,'selection_hyperpolarized.xlsx'))
    df_unselected.to_csv(join(table_folder,'failed_hyperpolarized.csv'))
    df_unselected.to_excel(join(table_folder,'failed_hyperpolarized.xlsx'))
