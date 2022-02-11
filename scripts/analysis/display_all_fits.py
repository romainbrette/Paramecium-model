'''
Make a big figure of all selected fits
'''
from brian2 import *
import os
from pylab import *
import matplotlib.pyplot as plt
import yaml
from scipy.signal import butter, sosfilt
from file_management import *
from plotting import *
import pandas as pd
from os.path import join, splitext, split
from fitting import *

choice = 3
v_range = None
if choice == 0:
    superimposed = True # If True, fits and data on the same panel
    t_max = 160
    filename = join(config['root'], 'Ciliated 4 mM KCl', 'tables', 'selection_hyperpolarized.csv')
    fit_name = 'hyperpolarized'
    aligned = False
elif choice == 1:
    superimposed = True
    t_max = 160
    filename = join(config['root'], 'Ciliated 4 mM KCl', 'tables', 'failed_hyperpolarized.csv')
    fit_name = 'hyperpolarized'
    aligned = False
elif choice == 2:
    superimposed = True
    t_max = 160
    v_range = (-40,80)
    filename = join(config['root'], 'Deciliated', 'tables', 'selection_deciliated.csv')
    fit_name = 'deciliated_bell_p2'
    aligned = False
elif choice == 3:
    superimposed = True
    t_max = 250
    v_range = (-40,80)
    filename = join(config['root'], 'Ciliated with PIV', 'tables', 'selection_ciliated.csv')
    fit_name = 'ciliated'
    aligned = True

folder = split(split(filename)[0])[0]
table = pd.read_csv(filename)
output_name = splitext(filename)[0]+'.pdf'

n = len(table)
m = int(sqrt(n)) # rows
p = int(n/m) # columns
if m*p<n:
    p+=1

if superimposed:
    fig = figure('Fits', (12,12))
else:
    fig = figure('Fits', (12,16))


for i, name in enumerate(table['name'][:n]):
    filename = join(folder, name)
    print(filename)

    # Load data
    data = rename_electrophysiology_data(load_multiple_data(filename, 'electrophysiology/data'))
    stimulus_start, stimulus_end = stimulus_time(one_protocol(filename))

    # Load fit data
    with open(os.path.join(filename, 'fits', fit_name+'.yaml'), 'r') as f:
        description = yaml.safe_load(f)

    # Trial selection
    if choice<3:
        select_trials(data, description['trials'])
    else: # We do it manually because of a previous bug in storing trial numbers
        I = amplitudes(data, stimulus_start, stimulus_end)
        select_trials(data, (I > -0.1 * nA) & (I < 5.01 * nA))

    # Alignment of traces on V0 = -22 mV
    if aligned:
        data['v'] = align_traces(data['v'], -22 * mV, data['t'] < stimulus_start)

    t, v, I = data['t'], data['v'], data['I']

    t = t-stimulus_start+20*ms

    # Run model
    Vfits = run_model(description['model'], data)['v']

    dt = t[1] - t[0]
    sos = butter(4, float(4000. * Hz), 'lp', fs=float(1 / dt), output='sos')  # 4th order Butterworth filter

    if superimposed:
        ax = fig.add_subplot(m,p,i+1)
    else:
        ax_trace = fig.add_subplot(2*m,p,(i % p) + int(i/p)*2*p+1)
        ax_fit = fig.add_subplot(2*m,p,(i%p)+ int(i/p)*2*p + p+1)

    j = 0
    traces, fits, Ipulses = [], [], []
    for Ii, Vi, Vfiti in zip(I, v, Vfits):
        if j%2 >= 0:
            filtered = sosfilt(sos, Vi / mV)
            if superimposed:
                ax.plot(t / ms, filtered, 'k')
                ax.plot(t / ms, Vfiti/mV, 'r')
            else:
                traces.append(filtered)
                fits.append(Vfiti/mV)
            Ipulses.append(mean(Ii[(t > 20 * ms) & (t < 120 * ms)]))
        j += 1

    # Plot
    if not superimposed:
        plot_curves(ax_trace, t/ms, traces, Ipulses)
        plot_curves(ax_fit, t/ms, fits, Ipulses)

    # Add cell number
    hyperpolarized = (array(Ipulses)<-1e-9).any()
    if hyperpolarized:
        position = -100
    else:
        position = 0

    if superimposed:
        ax.text(0,position,str(i+1),fontsize=15)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set_xlim(0, t_max)
    else:
        ax_fit.text(0,position,str(i+1),fontsize=15)
        ax_trace.spines['right'].set_visible(False)
        ax_trace.spines['top'].set_visible(False)
        ax_fit.spines['right'].set_visible(False)
        ax_fit.spines['top'].set_visible(False)
        ax_trace.set_xlim(0,t_max)
        ax_fit.set_xlim(0,t_max)

    if v_range is not None:
        if superimposed:
            ax.set_ylim(*v_range)
        else:
            ax_trace.set_ylim(*v_range)
            ax_fit.set_ylim(*v_range)
    elif hyperpolarized:
        if superimposed:
            ax.set_ylim(-150,0)
        else:
            ax_trace.set_ylim(-150,0)
            ax_fit.set_ylim(-150,0)
    else:
        if superimposed:
            ax.set_ylim(-40,40)
        else:
            ax_trace.set_ylim(-40,40)
            ax_fit.set_ylim(-40, 40)

fig.tight_layout()
fig.savefig(output_name)
