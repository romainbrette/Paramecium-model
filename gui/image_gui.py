'''
GUI for Paramecium movie processing
'''
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider, TextBox
import numpy as np

__all__ = ['image_gui']

def image_gui(parameters={}, callback=None, on_click=None):
    '''
    Produces a GUI that displays an array and parameter boxes.
    Changing a parameter calls the callback function with the dictionary of parameters.
    The callback function returns the image to be displayed.

    Returns the dictionary of parameters, with additionally the bounding box as
    x1, x2, y1, y2 (y=0 is the top).
    '''
    fig, ax0 = plt.subplots()
    plt.subplots_adjust(bottom=0.05*(len(parameters)+1))

    ax0.set_yticklabels([])
    ax0.set_xticklabels([])

    parameter_values = dict.fromkeys(parameters)

    def on_changed(event):
        for name in parameter_values:
            parameter_values[name] = button[name].val
        image = callback(parameter_values)
        image_object.set_data(image)

    ax = dict()
    button = dict()
    n = 0
    for name in parameters:
        x0, xmin, xmax = parameters[name]
        ax[name] = plt.axes([0.2, 0.025 + 0.05*n, .6, 0.05])
        button[name] = Slider(ax[name],name, xmin, xmax, valinit=x0)
        button[name].on_changed(on_changed)
        parameter_values[name] = x0
        n+=1

    def onclick(event):
        x, y = event.xdata, event.ydata
        img = on_click(x,y)
        if img is not None:
            image_object.set_data(img)
            fig.canvas.draw()

    if on_click is not None:
        cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # Display first image
    image = callback(parameter_values)
    if image.dtype==np.uint8:
        vmin,vmax=0,255
    elif image.dtype==np.uint16:
        vmin,vmax=0,65535
    elif image.dtype==np.float:
        vmin,vmax=0.,1.
    image_object = ax0.matshow(image, cmap='gray', vmin=vmin, vmax=vmax)

    plt.show()
    plt.close('all') # This doesn't seem to work

    parameter_values['x1'], parameter_values['x2'] = ax0.get_xbound()
    parameter_values['y1'], parameter_values['y2'] = ax0.get_ybound()

    return parameter_values