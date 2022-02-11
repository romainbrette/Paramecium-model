'''
Fitting ciliated cells, simultaneously to electrophysiology and particle flow angle.
With multifitting to enforce resting calcium concentration.

Note:
- for nans: debug with numpy.seterr(all='raise') (and numpy code generation)
'''
from file_management import *
from brian2 import *
from brian2modelfitting import MSEMetric
from fitting import *
from plotting import plot_fits
from brian2.units.constants import faraday_constant as F
from brian2.units.constants import gas_constant as R

savefits = False

path, display = fit_arguments(default='~/hodgkin/Paramecium/Electrophysiology/Selection - AP Model/Ciliated with PIV/2020-10-12 16.08.21 cell')

run_this_on_all_cells(path)

### Parameters
fitting_parameters = {'n_rounds': 100,
                      'n_samples': 100, # not too large for memory reasons
                      'n_refine_rounds': 2000}

### Model
model = load_models('Ie', 'IL', 'IV_K_ohmic', 'IK_bell_simple', 'IV_Ca_GHK', 'ICa_cilia_pCa',
                    'calcium_pump_and_diffusion_pCa',
                    'IKCa_instantaneous_pCa', 'electromotor_coupling_sincosangle_pCa')
model['constants'].update({'DV': R*((273 + 20.) * kelvin)/F,
                           'p_ICa': 2,
                           'EK': -48*mV})
model['bounds'].update({'C': [100*pF,200*pF,400*pF,500*pF],
                        'EL' : [-27*mV, -25*mV, -19*mV, -17*mV]}) # around -22 mV

# Add membrane equation
model['equations'] = membrane_equation(model['equations']) + model['equations']

# Get electrode parameters from previous fit
model['constants'].update(constants_from_file('taue','Re', path=path, name='electrode_and_RC'))

### Data loading selection
# Load and rename variables
data = rename_electrophysiology_data(load_multiple_data(path,'electrophysiology/data'))
piv = load_multiple_data(path,'piv_analysis/analysis')

# Optional: subsampling to 10 kHz
# subsample(data, 4)

# Trial selection
stimulus_start, stimulus_end = stimulus_time(one_protocol(path))
I = amplitudes(data, stimulus_start, stimulus_end)
fitting_parameters['trials'] = select_trials(data, (I>-0.1*nA) & (I<5.01*nA))
select_trials(piv, (I>-0.1*nA) & (I<5.01*nA))

# Angle relative to cell angle, then interpolate to the electrophysiology acquisition rate
angle = piv['angle_mean']
cell_angle = corrected_cell_angle(cell_orientation(path), angle[:,:3]) # use the first 3 frames to calculate piv angle
interpolated = interpolate_piv(data, {'cos': cos(angle-cell_angle), 'sin': sin(angle-cell_angle)})
data['cos_angle'] = interpolated['cos']
data['sin_angle'] = interpolated['sin']

# Temporal selection
trim_data(data, stimulus_end+500*ms)

# Alignment of traces on V0 = -22 mV
data['v'] = align_traces(data['v'], -22*mV, data['t']<stimulus_start)

# Target calcium concentration (enforced before stimulus start)
data['pCa'] = zeros_like(data['v'])

### Fitting
# Metrics (mean squared error with normalization)
# Note: t_weights are normalized by their mean
t = data['t']
weights_v = ((t>stimulus_start) & (t<stimulus_end))*1 + ((t>stimulus_end) & (t<stimulus_end+500*ms))*0.2
weights_pCa = (t>stimulus_start-100*ms) & (t<stimulus_start)
metrics = {'v': MSEMetric(t_weights=weights_v, normalization=1*mV),
           'pCa' : MSEMetric(t_weights=weights_pCa, normalization=1),
           'cos_angle': MSEMetric(t_start=stimulus_start-100*ms, normalization=1),
           'sin_angle': MSEMetric(t_start=stimulus_start-100*ms, normalization=1)}

fits, best_params, results = two_stage_fit(model=model, data=data, metrics=metrics, **fitting_parameters)

# Write to file
write_fit_file(results, path)

if savefits:
    save_fits({var: fits[var] for var in metrics}, path, trials=fitting_parameters['trials'])

### Display
if display:
    plot_fits(data, fits, metrics=metrics)
    show()
