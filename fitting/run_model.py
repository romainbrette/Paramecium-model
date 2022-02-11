'''
Runs an optimized model on data
'''

from brian2 import *
from brian2.units.constants import faraday_constant as F
from brian2.units.constants import gas_constant as R
from brian2modelfitting import *
from file_management import build_model

set_device('cpp_standalone', directory=None)

__all__ = ['run_model']

def run_model(description=None, data=None):
    '''
    Runs an optimized model on the data.
    Returns all variables as a dictionary.
    '''
    eqs, init, _ = build_model(description)

    ### Data
    t = data['t']
    dt = t[1]-t[0]
    V = data['v']
    I = data['I']

    # Generate traces
    fitter = TraceFitter(model=eqs,
                         input={'I' : I},
                         output={'v' : V}, dt=dt,
                         n_samples=1,
                         param_init=init,
                         method='euler')

    fits = fitter.generate(params={}, output_var=eqs.eq_names) # all state variables

    return fits
