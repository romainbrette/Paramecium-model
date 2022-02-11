'''
Selection of data
'''
import yaml
import os
from brian2 import second
import numpy as np
from numpy import mean

__all__ = ['trim_data', 'stimulus_time', 'amplitudes', 'select_trials', 'merge_data', 'align_traces', 'subsample']

def subsample(data, n):
    '''
    Subsamples the data n times.
    '''
    data['t'] = data['t'][::n]
    for var in data:
        if (var != 't') & (var != 'trigger'):
            data[var] = data[var][:,::n]

    # Triggers are more complicated!
    ntrials = data['trigger'].shape[0]
    new_trigger = np.zeros((ntrials,len(data['t'])))
    for i in range(ntrials):
        trigger_i = (data['trigger'][i]>0).nonzero()[0]
        new_trigger[i,:] = np.zeros(len(data['t']))
        new_trigger[i,(trigger_i/n).astype(int)] = 1
    data['trigger'] = new_trigger

def align_traces(v, v0, selection):
    '''
    Align traces on v0, by measuring resting potential on the period given by `selection`
    '''
    V0 = (v[:, selection]).mean(axis=1)
    v += (v0 - V0).reshape((len(V0), 1))
    return v

def merge_data(data):
    '''
    Merges a list of data sets.
    `t` is taken from the last trial (thus, assumed identical in all trials).
    '''
    dataset = {}
    for single_set in data:
        for x, value in single_set.items():
            if (len(value.shape) == 1) or (x not in dataset):
                dataset[x] = value
            else: # assuming 2
                dataset[x] = np.vstack([dataset[x], value])
    return dataset

def trim_data(data, t_end):
    '''
    Trimming in place: all data are cut at t<t_end
    '''
    t = data['t']
    data['t'] = data['t'][t < t_end]
    for var in data:
        if var != 't':
            data[var] = data[var][:, t < t_end]

def stimulus_time(path):
    '''
    Returns stimulus start and end times from the protocol folder (with units).
    '''
    with open(os.path.join(path, 'protocol.yaml'), 'r') as fp:
        d = yaml.safe_load(fp)
    return d['start']*second, d['end']*second

def amplitudes(data, stimulus_start, stimulus_end):
    '''
    Returns mean value of I during the stimulus in all trials.
    '''
    t = data['t']
    return mean(data['I'][:, (t >= stimulus_start) & (t <= stimulus_end)], axis=1)

def select_trials(data, selection):
    '''
    Selects all trials indexed by selection, or for which selection is True.
    Returns the indices of selected trials.
    '''
    for var in data:
        if var != 't':
            data[var] = data[var][selection, :]

    if isinstance(selection, list):
        return selection
    else:
        return [int(x) for x in selection.nonzero()[0]]