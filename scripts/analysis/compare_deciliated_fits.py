'''
Compares the quality of different models for deciliated fits.
'''
import pandas as pd
from scipy.stats import wilcoxon
from file_management.configuration import *
from os.path import join

table_folder = join(join(config['root'],'Deciliated'), 'tables')

models = ['deciliated_bell', 'deciliated_bell_p2', 'deciliated_simple', 'deciliated_simpler', 'deciliated_HH', 'deciliated_HH_p2']

errors = []
for model in models:
    print(model)
    # Make the panda table
    df = pd.read_csv(join(table_folder,model+'.csv'))
    print(len(df),'cells')
    print('Error: {} mV (median), {} mV (mean) +- {} mV (s.d.)'.format(1000*((df['error_v']**.5).median()),
                                                                       1000*((df['error_v']**.5).mean()),
                                                                       1000*((df['error_v']**.5).std())))
    for x in ['p_IK', 'a_IK', 'taumin_IK', 'b_IK']:
        try:
            print(df[x].describe())
            print()
        except KeyError:
            pass

    print()
    errors.append(df['error_v'])

print('Two-tailed Wilcoxon test')
for i in range(len(models)):
    for j in range(i+1,len(models)):
        try:
            _, p = wilcoxon(errors[i],errors[j])
            print(models[i],'({}) !='.format(errors[i].median()),models[j],'({})'.format(errors[j].median()),': p = ',p)
        except ValueError:
            pass

print()
print('One-tailed Wilcoxon test')
for i in range(len(models)):
    for j in range(len(models)):
        if i!=j:
            try:
                _, p = wilcoxon(errors[i],errors[j],alternative='greater')
                print(models[i],'({}) >'.format(errors[i].median()),models[j],'({})'.format(errors[j].median()),': p = ',p)
            except ValueError:
                pass
