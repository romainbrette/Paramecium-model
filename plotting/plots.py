'''
Plots
'''
from matplotlib import cm
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import matplotlib.pyplot as plt
from brian2 import second, ms
from pylab import *

__all__ = ['plot_curves', 'prepare_panel', 'scale_bar', 'plot_fits']

def plot_fits(data, fits, metrics=None, vars=None):
    '''
    Plots fits to data (superimposed) for variables `vars` (or all variables in `fits`).
    The time axis is shared between subplots.
    `metrics` provide a normalization factor and a start time.
    '''
    if vars is None:
        if metrics is None:
            vars = fits.keys()
        else:
            vars = metrics.keys()

    if metrics is None:
        units = {var:1 for var in vars}
        t_start = 0*second
    else:
        units = {var: metrics[var].normalization for var in vars}
        t_start = metrics[list(metrics.keys())[0]].t_start

    t = data['t']

    n = len(vars)
    fig, axes = plt.subplots(n, 1, sharex=True)
    if n == 1:
        axes = [axes]
    for i, name in enumerate(vars):
        for Vi, Vfit in zip(data[name], fits[name]):
            axes[i].plot(t/ms, Vi*units[name], 'k')
            axes[i].plot(t/ms, Vfit*units[name], 'r')
        axes[i].set(ylabel=name)
        axes[i].set_xlim(t_start/ms, t[-1]/ms)
    xlabel('Time (ms)')
    tight_layout()

def plot_curves(ax, t, curves, index = None, cmap=None, color_shift=0., revert=False):
    '''
    Plots curves with a color map.
    If index is provided, it is used to order the curves.
    '''
    alpha = 1.
    if cmap is None:
        cmap = cm.rainbow
        alpha = 0.5
    n = len(curves)
    if index is not None:
        _, curves = zip(*sorted(zip(index, curves)))
    for i,curve in enumerate(curves):
        if revert:
            ax.plot(t, curve, color=cmap(1-(i+color_shift*n)/(n+color_shift*n)), alpha=alpha)
        else:
            ax.plot(t, curve, color=cmap((i+color_shift*n)/(n+color_shift*n)), alpha=alpha)

def prepare_panel(ax):
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

def scale_bar(ax, size, text):
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])
    scalebar = AnchoredSizeBar(ax.transData,
                               size, text, 'lower right',
                               frameon=False)
    ax.add_artist(scalebar)
