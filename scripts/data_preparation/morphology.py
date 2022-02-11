'''
Manual measurement of cells

Argument: cell folder, or folder with cell folders

The user points:
- anterior
- posterior
- ventral
- dorsal
Of course there might be confusions.

The results are saved in a yaml file.
- anterior, posterior, ventral, dorsal : (x,y) list of coordinates in pixels
- pixel_width: pixel width in um
- major, minor: major and minor axis in um
'''
from gui import image_gui
import os
import imageio
import yaml
from skimage.draw import circle
import sys
from file_management.batch_processing import *

overwrite = False

# Parse command line arguments
args = sys.argv
path = args[1]

folders = cell_folders(path, recursive=True)

for cell_folder in folders:
    cell_filename = os.path.join(cell_folder,'cell.tiff')
    morphology_filename = os.path.join(cell_folder,'morphology.yaml')

    if os.path.exists(cell_filename):
        if overwrite or (not os.path.exists(morphology_filename)):
            print(cell_folder)

            # Find a yaml file with pixel width information
            folders = protocol_folders(cell_folder, recursive=False)
            for folder in folders:
                try:
                    with open(os.path.join(folder,'protocol.yaml')) as f:
                        pixel_width = yaml.load(f)['camera_parameters']['pixel_width']
                except:
                    pixel_width = None

            # Load image
            image = imageio.imread(cell_filename)

            # GUI
            def update_parameters(parameters):
                return image

            feature_coords = []

            original_image = image.copy()
            M = image.max()

            def pick_feature(x, y):
                global feature_coords

                if len(feature_coords) == 4: # Reset on the 5th click
                    feature_coords = []
                    image[:] = original_image
                feature_coords.append([float(x), float(y)])
                rr, cc = circle(int(y), int(x), 5, shape=image.shape)
                image[rr, cc] = M

                return image

            image_gui(parameters={},
                      callback=update_parameters,
                      on_click=pick_feature)

            if len(feature_coords) == 4:
                # Save: image, pixel positions, pixel width, measurement calculations (axis, membrane area)
                # paramecium_manual_measurement
                info = {'pixel_width' : pixel_width}
                info['anterior'], info['posterior'], info['ventral'], info['dorsal'] = feature_coords

                x1, y1 = feature_coords[0]
                x2, y2 = feature_coords[1]
                x3, y3 = feature_coords[2]
                x4, y4 = feature_coords[3]

                if pixel_width is not None:
                    info['major'] = pixel_width*((x2-x1)**2+(y2-y1)**2)**.5  # in um
                    info['minor'] = pixel_width*((x4-x3)**2+(y4-y3)**2)**.5  # in um

                with open(morphology_filename,'w') as f:
                    yaml.dump(info,f)
