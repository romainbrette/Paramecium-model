'''
Plotting cell and cilia movement
'''
import numpy as np
from skimage.draw import polygon, circle

__all__ = ['cell_border', 'plot_cell', 'cell_mask', 'cell_indices']

cell_length = 120.
cell_width = 35.

def cell_border(theta = 0.):
    '''
    Returns cell coordinates in um, centered on 0.
    The cell points towards the right.
    '''
    # Shape coordinates
    asymetry = 0.15
    xcell = np.linspace(-cell_length*.5,cell_length*.5,150)
    ycell = .5*cell_width*((1-4*xcell**2/cell_length**2)**.5 - asymetry*np.sin(np.pi*2*xcell/cell_length))
    ycell = np.hstack([ycell,-ycell[::-1]])
    xcell = np.hstack([xcell,xcell[::-1]])

    xshape = xcell * np.cos(theta) - ycell * np.sin(theta)
    yshape = xcell * np.sin(theta) + ycell * np.cos(theta)

    return xshape, yshape

def cell_mask(x, y, image, pixel_size=1., theta = 0.):
    '''
    Returns a binary mask for the cell shape, into `image`.
    `pixel_size` is the size of a pixel in um.
    `x` and `y` are the position in um.

    Note : y = 0 is at the bottom
    '''
    xshape, yshape = cell_border(theta)
    xshape = ((x + xshape)/pixel_size).astype(int)
    yshape = ((y + yshape)/pixel_size).astype(int)
    rr, cc = polygon(yshape,xshape, shape=image.shape)
    rr = image.shape[0]-1 - rr

    new_image = np.zeros_like(image)
    new_image[:, :][rr, cc] = 1
    return new_image

def cell_indices(x, y, image, pixel_size=1., theta = 0.):
    '''
    Returns the coordinates of the cell shape, in `image`.
    `pixel_size` is the size of a pixel in um.
    `x` and `y` are the position in um.

    Note : y = 0 is at the bottom
    '''
    xshape, yshape = cell_border(theta)
    xshape = ((x + xshape)/pixel_size).astype(int)
    yshape = ((y + yshape)/pixel_size).astype(int)
    rr, cc = polygon(yshape,xshape, shape=image.shape)
    rr = image.shape[0]-1 - rr

    return rr, cc


def plot_cell(ax, x,y,scale, theta = 0., **kwds):
    '''
    Plots a cell at position (x,y) with the given scale (= length in y units).

    TODO: scale relative to actual fig size
    '''

    xcell, ycell = cell_border(theta=theta) # pointing up
    xcell = np.hstack([xcell,[xcell[0]]]) / cell_length
    ycell = np.hstack([ycell,[ycell[0]]]) / cell_length

    ax.plot(x+scale*xcell, y+scale*ycell, **kwds)

if __name__ == '__main__':
    from pylab import *

    if False:
        image = zeros((500,500))
        imshow(cell_mask(200,200,image, pixel_size=2., theta = pi/2.))
        show()
    else:
        figure()
        ax = subplot(111)
        plot_cell(ax, 0,0,1, color='k')
        xlim(-0.5,0.5)
        ylim(-0.5,0.5)
        xticks()
        yticks()
        savefig('cell_shape.pdf')
        show()
