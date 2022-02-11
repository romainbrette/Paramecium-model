'''
A linear model with one electrode and neuron, no drift.
We fit it to small stimulations.
This is used to get electrode parameters.
'''
from file_management import *
from brian2 import *
from brian2modelfitting import MSEMetric
from fitting import *
from plotting import plot_fits

path, display = fit_arguments(default='~/Paramecium data/2020-10-28 17.46.05 cell')

run_this_on_all_cells(path)

### Parameters
fitting_parameters = {'n_rounds' : 50,
                      'n_samples' : 50,
                      'n_refine_rounds' : 200}

### Model
model = {'equations': '''
                       dv/dt = (-(v-EL)/Rm + Ie)/C : volt
                       dv2/dt = (v-v2+tip+Re*I)/taue : volt
                       Ie = (v2-tip-v)/Re : amp
                       ''',

         'bounds': {
             'EL': [-60 * mV, -60 * mV, 0 * mV, 10 * mV],
             'tip': [-30 * mV, -30 * mV, 30 * mV, 30 * mV],
             'Rm': [10 * Mohm, 10 * Mohm, 300 * Mohm, 500 * Mohm],
             'Re': [1 * Mohm, 10 * Mohm, 300 * Mohm, 500 * Mohm],
             'taue': [0.05 * ms, 0.1 * ms, 5 * ms, 5 * ms],
             'C': [30 * pF, 200 * pF, 500 * pF, 500 * pF]},

         'init': {
             'v': 'EL',
             'v2': 'EL + tip'}
         }

### Data loading selection
# Load and rename variables
data = rename_electrophysiology_data(load_multiple_data(path,'electrophysiology/data'))

# Temporal selection
stimulus_start, stimulus_end = stimulus_time(one_protocol(path))
trim_data(data, stimulus_end+100*ms)

# Trial selection
fitting_parameters['trials'] = select_trials(data, abs(amplitudes(data, stimulus_start, stimulus_end))<.5*nA)

### Fitting
# Metrics (mean squared error with normalization)
metrics = {'v': MSEMetric(t_start=stimulus_start-100*ms, normalization=1*mV),
           'v2': MSEMetric(t_start=stimulus_start-100*ms, normalization=1*mV)}

fits, best_params, results = two_stage_fit(model=model, data=data, metrics=metrics, **fitting_parameters)

# Write to file
write_fit_file(results, path)

### Display
if display:
    plot_fits(data, fits, metrics=metrics)
    show()
