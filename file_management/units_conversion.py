'''
Input/output utilities
'''
from brian2 import *

__all__ = ['dictionary_units_to_str', 'dictionary_str_to_number', 'units_to_str']

def units_to_str(x):
    '''
    Converts x with units to strings for saving.
    '''
    if isinstance(x, str) or is_dimensionless(x):
        return x
    else:
        return str(float(x)) + ' * ' + repr(x.dim)

def dictionary_units_to_str(d):
    '''
    Converts the values of d with units to strings for saving.
    '''
    new_d = dict()
    for key, value in d.items():
        if isinstance(value,str) or is_dimensionless(value):
            new_d[key] = value
        else:
            new_d[key] = str(float(value)) + ' * ' + repr(value.dim)
    return new_d

def dictionary_str_to_number(d, namespace=None):
    '''
    Converts the string values of d to numbers, possibly with units
    '''
    return {x: eval(d[x]) for x in d}