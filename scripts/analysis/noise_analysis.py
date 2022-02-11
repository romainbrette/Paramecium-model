'''
Analysis of noise in ciliated cells, 4 mM KCl

The script examines portions of signals before stimulus start (300 ms), where the stimulus is a positive pulse
(to avoid prolonged hyperpolarizations after a negative pulse).

The model is: V_measured = V_cell + noise
where the noise is independent between the two electrodes.
Then cov(V1, V2) = intrinsic variance of cell Vm.
'''
from brian2 import *
from file_management import *
import pandas as pd
from os.path import join, splitext, split
import numpy as np

filename = join(config['root'], 'Ciliated 4 mM KCl', 'tables', 'selection_hyperpolarized.csv')

folder = split(split(filename)[0])[0]
table = pd.read_csv(filename)

M = []
M_LT = [] # LT for long-term
for i, name in enumerate(table['name']):
    filename = join(folder, name)
    print(filename)

    # Load data
    data = rename_electrophysiology_data(load_multiple_data(filename, 'electrophysiology/data'))
    stimulus_start, stimulus_end = stimulus_time(one_protocol(filename))
    I = amplitudes(data, stimulus_start, stimulus_end)
    select_trials(data, I > 0 * nA) # Otherwise we get prolonged hyperpolarizations
    t, v, v2 = data['t'], data['v']/mV, data['v2']/mV

    M.append(np.mean([np.cov(v[i,t<stimulus_start], v2[i,t<stimulus_start]) for i in range(v.shape[0])], axis=0))
    M_LT.append(np.cov(v[:, t < stimulus_start].flatten(), v2[:, t < stimulus_start].flatten()))

M = np.mean(M, axis=0)
M_LT = np.mean(M_LT, axis=0)

print('Short-term fluctuations (<300 ms)')
print('Intrinsic noise: {} mV'.format(M[0,1]**.5))
print('Experimental noise, reading electrode: {} mV'.format((M[0,0]-M[0,1])**.5))
print('Experimental noise, injecting electrode: {} mV'.format((M[1,1]-M[0,1])**.5))
print()
print('Long-term fluctuations (~ 60s)')
print('Intrinsic noise: {} mV'.format(M_LT[0,1]**.5))
print('Experimental noise, reading electrode: {} mV'.format((M_LT[0,0]-M_LT[0,1])**.5))
print('Experimental noise, injecting electrode: {} mV'.format((M_LT[1,1]-M_LT[0,1])**.5))
