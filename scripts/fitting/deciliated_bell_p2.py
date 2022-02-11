'''
Ohmic IK model with bell-type time constant, for fitting depolarized responses in deciliated cells.
p = 2 and baseline time constant nearly 0.
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
fitting_parameters = {'n_rounds' : 150,
                      'n_samples' : 100,
                      'n_refine_rounds' : 2000}

### Model
model = load_models('Ie', 'IL', 'IV_K_ohmic', 'IK_bell')
model['constants'].update({'DV': R*((273 + 20.) * kelvin)/F,
                           'p_IK': 2,
                           'a_IK': 0.1 * ms})

# Add membrane equation
model['equations'] = membrane_equation(model['equations']) + model['equations']

# Get electrode parameters from previous fit
model['constants'].update(constants_from_file('taue','Re','EK','C', path=path, name='hyperpolarized'))

### Data loading selection
# Load and rename variables
data = rename_electrophysiology_data(load_multiple_data(path,'electrophysiology/data'))

# Temporal selection
stimulus_start, stimulus_end = stimulus_time(one_protocol(path))
trim_data(data, stimulus_end+50*ms)
t = data['t']

# Trial selection
I = amplitudes(data, stimulus_start, stimulus_end)
fitting_parameters['trials'] = select_trials(data, (I>0*nA) & (I<4.01*nA))

### Fitting
# Metrics (mean squared error with normalization)
# Weights are chosen so that the onset and the rest are equally weighted
t_weights = ((t>stimulus_start) & (t<stimulus_start+30*ms))*(1/3-1/17) + (t>stimulus_start-50*ms)/17
metrics = {'v': MSEMetric(t_weights=t_weights, normalization=1*mV)}
#metrics = {'v': MSEMetric(t_start=stimulus_start-50*ms, normalization=1*mV)}

fits, best_params, results = two_stage_fit(model=model, data=data, metrics=metrics, **fitting_parameters)

# Write to file
write_fit_file(results, path)

### Display
if display:
    plot_fits(data, fits, metrics=metrics)
    show()
