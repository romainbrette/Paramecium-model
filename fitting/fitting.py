'''
Tools for model fitting.
This requires brian2modelfitting.
'''
import numpy as np
from file_management import *
import yaml
from brian2 import *
from brian2modelfitting import *
import os
import inspect
import datetime
from time import time
import sys
from brian2.units.constants import faraday_constant as F
from brian2.units.constants import gas_constant as R

__all__ = ['global_error', 'local_error', "write_fit_file", 'two_stage_fit', 'fit_arguments', 'constants_from_file',
           'save_fits']

set_device('cpp_standalone', directory=None)

def fit_arguments(default=None):
    '''
    Returns command line argument: path (with default).
    Also returns display flag: True for the default path, False otherwise.
    '''
    if len(sys.argv) > 1:
        path = sys.argv[1]
        display = False
    else:
        path = os.path.expanduser(default)
        display = True
    return path, display

def two_stage_fit(model=None, data=None, metrics=None,
                  n_samples=50, n_rounds=100, n_refine_rounds=2000,
                  input_vars=['I'], **fitting_parameters):
    '''
    Runs fitting procedure in two stages: differential evolution followed by gradient descent.
    '''
    # Build model

    eqs, init, bounds = build_model(model)
    fitting_parameters.update({'n_samples': n_samples, 'n_rounds': n_rounds, 'n_refine_rounds': n_refine_rounds})

    # Split bounds
    bounds_DE = {} # for differential evolution
    bounds_refine = {} # for gradient descent
    for var, value in bounds.items():
        if len(bounds[var])==2:
            bounds_DE[var] = bounds[var].copy()
            bounds_refine[var] = bounds[var].copy()
        else: # assuming 4
            bounds_DE[var] = [bounds[var][1],bounds[var][2]]
            bounds_refine[var] = [bounds[var][0],bounds[var][3]]

    # Run fitting
    t = data['t']
    output_vars = list(metrics.keys())

    fitter = TraceFitter(model=eqs, output={key: data[key] for key in output_vars},
                         input={var: data[var] for var in input_vars}, dt=t[1] - t[0],
                         n_samples=n_samples, param_init=init, method='euler')

    t1 = time()
    print("*** Phase 1: differential evolution ***")
    _, error = fitter.fit(n_rounds=n_rounds, optimizer=NevergradOptimizer(method='TwoPointsDE'),
                          metric=metrics, callback='text', **bounds_DE)
    print('Error (phase 1) = {} mV'.format(error ** .5))
    print()

    # Refine
    print("*** Phase 2: gradient descent ***")
    best_params, result = fitter.refine(maxfev=n_refine_rounds, calc_gradient=True,
                                        **bounds_refine)  # nan_policy = 'omit'
    t2 = time()
    print('Fitting took {} s'.format(t2 - t1))
    error = global_error(result)
    print('Error = {} mV'.format(error))

    # Traces
    fits = fitter.generate_traces(params=best_params)
    if len(output_vars) == 1:
        fits = {output_vars[0]: fits}

    # Clean up
    device.delete()

    # Produce information dictionary
    fitting_start = metrics[list(metrics.keys())[0]].t_start
    fitting_end = t[-1]
    results = {'fitting_start': float(fitting_start), 'fitting_end': float(fitting_end)}
    results.update(fitting_parameters)

    # Model with fitted parameters
    if 'constants' not in model:
        model['constants'] = {}
    model['constants'].update(best_params)
    model['constants'] = dictionary_units_to_str(model['constants'])
    del model['bounds']  # not useful
    results['model'] = model

    # Results
    results['error'] = float(error)
    results['errors'] = local_error(data, fits, output_vars, fitting_start)

    return fits, best_params, results

def global_error(result):
    '''
    Returns the error of the fit, using weights and normalization.
    '''
    return np.mean(result.fun ** 2) ** .5

def local_error(data, fits, vars, stimulus_start):
    '''
    Calculates the error for each output variable
    '''
    errors = {}
    dt = data['t'][1] - data['t'][0]
    for var in vars:
        x = data[var][:, int(stimulus_start / dt):]
        errors[var] = float(((fits[var][:, int(stimulus_start / dt):] - x) ** 2).mean())  # maybe normalize
    return errors

def write_fit_file(info, path, name=None):
    '''
    Writes the info file to path/fits/caller_file.yaml
    Adds file name and date.
    '''
    fit_folder = make_subdir(path, 'fits')
    if name is None:
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = os.path.splitext(os.path.split(module.__file__)[1])[0]
    output_name = os.path.join(fit_folder, name+'.yaml')  # could be extracted from the script filename

    info['name'] = name
    info['date'] = datetime.datetime.now().isoformat()

    with open(output_name, 'w') as fp:
        yaml.dump(info, fp)

def save_fits(fits, path, name=None, trials=None):
    '''
    Save fits to disk.
    `trials` (optionally) gives the list of trial indices.
    '''
    if name is None: # Get name from calling script
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        name = os.path.splitext(os.path.split(module.__file__)[1])[0]
    data_folder = make_subdir(os.path.join(path,'fits'), name)

    # Saving: could be refactored in clampy
    variables = list(fits.keys())
    header = ' '.join(variables)
    ntrials = fits[variables[0]].shape[0]
    if trials is None:
        trials = range(ntrials)
    for i in range(ntrials):
        M = np.vstack([value[i] for value in fits.values()]).T
        np.savetxt(os.path.join(data_folder, 'fits{:03d}.txt.gz'.format(trials[i])), M, header=header, comments='')

def constants_from_file(*vars, path=None, name=None):
    '''
    Gets constants from a fit results file, and evaluates them.
    '''
    with open(os.path.join(path, 'fits/'+name+'.yaml'), 'r') as fp:
        fit_results = yaml.safe_load(fp)
    return dictionary_str_to_number({var: fit_results['model']['constants'][var] for var in vars})
