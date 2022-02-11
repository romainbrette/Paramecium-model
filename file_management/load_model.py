'''
Loads and builds a model description from a yaml description.

TODO: load_models could be made more general
'''
import yaml
import os
from brian2 import *
from brian2.units.constants import faraday_constant as F
from brian2.units.constants import gas_constant as R
import re

__all__ = ['load_models', 'build_model', 'membrane_equation']

# Paths
current_path = os.path.split(os.path.realpath(__file__))[0]  # folder of this script
package_path = os.path.split(current_path)[0]  # main package
model_path = os.path.join(package_path, 'models')

def membrane_equation(equations):
    '''
    Returns a membrane equation as string.
    '''
    eqs = Equations(equations)
    # Find all currents
    currents = []
    for var in eqs.diff_eq_names.union(eqs.eq_names):
        if eqs[var].unit == amp:
            currents.append(var)
    return 'dv = ('+'+'.join(currents)+')/C : volt/second\n' + \
            'dv/dt = dv : volt\n'

def load_models(*names, verbose=False):
    '''
    Loads model descriptions from multiple files in the model library.
    Returns a dictionary with equations (string), init (dictionary), constants (dictionary), bounds (dictionary).
    Constants and bounds are evaluated.
    '''
    all_equations = ''
    all_bounds = {}
    all_init = {}
    all_constants = {}
    for name in names:
        if verbose:
            print('Including ' + name)
        name = os.path.join(model_path, 'components', name) + '.yaml'
        with open(name, 'r') as fp:
            description = yaml.safe_load(fp)
        bounds = description.get('bounds',{})
        constants = description.get('constants',{})

        # Evaluate bounds
        bounds_evaluated = {}
        for var, value in bounds.items():
            bounds_evaluated[var] = bounds[var].copy()
            for i in range(len(bounds[var])):
                if isinstance(value[i], str):
                    bounds_evaluated[var][i] = eval(value[i])

        # Evaluate constants
        constants_evaluated = {}
        for var, value in constants.items():
            if isinstance(value, str):
                constants_evaluated[var] = eval(value)
            else:
                constants_evaluated[var] = value

        all_equations += description['equations'] + "\n"
        all_bounds.update(bounds_evaluated)
        all_init.update(description.get('init',{}))
        all_constants.update(constants_evaluated)

    # Remove duplicate endlines
    all_equations = re.sub(r'(\n+)', r'\n', all_equations)

    return {'equations': all_equations,
            'init': all_init,
            'constants': all_constants,
            'bounds': all_bounds}


def build_model(model=None):
    '''
    Builds a model from a dictionary, as returned by `load_model`.
    Returns eqs, init, bounds_DE, bounds_refine
    '''
    equations = model.get('equations', '')
    init = model.get('init', {}).copy()
    constants = model.get('constants', {})
    bounds = model.get('bounds', {})

    ### Build model
    # Constants overwrite bounds
    for constant in constants:
        if constant in bounds:
            del bounds[constant]

    # Evaluate constants
    constants_evaluated = {}
    for var, value in constants.items():
        if isinstance(value, str):
            constants_evaluated[var] = eval(value)
        else:
            constants_evaluated[var] = value

    # Make equations
    eqs = Equations(equations, **constants_evaluated)
    # Add parameters specified in bounds to the equations
    for var, value in bounds.items():
        try:
            unit = value[0].dim
        except AttributeError:
            unit = 1
        eqs += Equations(var + ' : ' + unit.__repr__() + ' (constant)')

    # Replace constants in init
    for key in init.keys():
        try:
            if isinstance(init[key],str):
                init[key] = eval(init[key], constants_evaluated.copy())
        except NameError: # could be in bounds
            pass

    return eqs, init, bounds
