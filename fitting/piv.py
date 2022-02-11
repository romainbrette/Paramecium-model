'''
Tools for PIV analysis.
'''
import numpy as np
from scipy.stats import circmean

__all__ = ['interpolate_piv', 'corrected_cell_angle', 'reversal_duration']

def reversal_duration(angle, start=None):
    '''
    Returns the duration of reversal from the angle sequence, in time steps.
    The angle is assumed to be relative to the cell angle.
    Reversal is when cos(angle) changes sign.
    '''
    try:
        if start is None:
            start = (np.cos(angle)<0).nonzero()[0][0]
        return (np.cos(angle[start:])>0).nonzero()[0][0]
    except IndexError:
        return 0

def interpolate_piv(data, analysis):
    '''
    Linear interpolation of data in the `analysis` dictionary to the times in `data`, assuming
    `data['trigger']` contains the triggers of the images analyzed in `analysis`.
    `analysis` can also be an array for a single variable.
    '''
    ### Get trigger
    t, trigger = data['t'], data['trigger'][0] # this could fail if no trigger
    trigger_times = t[trigger > 0]
    frame_times = .5*(trigger_times[:-1] + trigger_times[1:])

    ### Interpolate - could fail if the number of recorded frames is wrong
    single_variable = False
    if isinstance(analysis, np.ndarray):
        analysis = {'0' : analysis}
        single_variable = True

    interpolated = {}
    for var, value in analysis.items():
        if (np.sum(np.isnan(value)) > 0):
            interpolated[var] = np.array([np.interp(t, frame_times[~np.isnan(yi)], yi[~np.isnan(yi)]) for yi in value])
        else:
            interpolated[var] = np.array([np.interp(t, frame_times, yi) for yi in value])

    if single_variable:
        interpolated = interpolated['0']

    return interpolated

def corrected_cell_angle(cell_angle, piv_angle):
    '''
    Flip the cell_angle (anterior <-> posterior) if the PIV field points to the opposite direction.
    '''
    piv_angle = piv_angle.flatten()
    angle0 = circmean(piv_angle[~np.isnan(piv_angle)], np.pi, -np.pi)
    if np.cos(angle0 - cell_angle) < 0:
        cell_angle = cell_angle + np.pi  # anterior-posterior flip
    return cell_angle
