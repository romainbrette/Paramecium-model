'''
A simple model of hyperpolarized responses: IK, IKir, Ie.
Simplified model with p=2.
'''
from file_management import *
from brian2 import *
from brian2modelfitting import MSEMetric
from fitting import *
from plotting import plot_fits
from brian2.units.constants import faraday_constant as F
from brian2.units.constants import gas_constant as R

path, display = fit_arguments(default='~/Paramecium data/2020-10-28 17.46.05 cell')

run_this_on_all_cells(path)

### Parameters
fitting_parameters = {'n_rounds' : 50,
                      'n_samples' : 100,
                      'n_refine_rounds' : 500}

### Model
model = load_models('Ie', 'IL', 'IV_K_ohmic', 'IKir')
model['constants'].update({'DV' : R*((273 + 20.) * kelvin)/F,
                           'p_IKir' : 1})
model['bounds'].update({'C': [100*pF, 100*pF, 500*pF, 500*pF]})

# Add membrane equation
model['equations'] = membrane_equation(model['equations']) + model['equations']

# Get electrode parameters from previous fit
model['constants'].update(constants_from_file('taue','Re', path=path, name='electrode_and_RC'))

### Data loading selection
# Load and rename variables
data = rename_electrophysiology_data(load_multiple_data(path,'electrophysiology/data'))

# Temporal selection
stimulus_start, stimulus_end = stimulus_time(one_protocol(path))
trim_data(data, stimulus_end+50*ms)

# Trial selection
fitting_parameters['trials'] = select_trials(data, amplitudes(data, stimulus_start, stimulus_end)<0*nA)

### Fitting
# Metrics (mean squared error with normalization)
metrics = {'v': MSEMetric(t_start=stimulus_start-50*ms, normalization=1*mV)}

fits, best_params, results = two_stage_fit(model=model, data=data, metrics=metrics, **fitting_parameters)

# Write to file
write_fit_file(results, path)

### Display
if display:
    plot_fits(data, fits, metrics=metrics)
    show()
