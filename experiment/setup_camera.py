'''
Set up the Lumenera camera
'''
import warnings

__all__ = ['setup_camera', 'camera_parameters']

camera_parameters = {
    'name': 'INFINITY3-6UR',
    'total_width': 2752,  # 490 * 390 um
    'total_height': 2192,
    'ROI_width': int(130 * 5.63),  # 130 um
    'ROI_height': int(130 * 5.63),
    'exposure': 1.19,
    'gain': 0.57,
    'binning': 8,
    'pixel_width': 1. / 5.63, # in um; assuming x40 and no binning; this is then multiplied by binning (below)
    'depth': 8,
    'frame_debug': False,  # whether to include the frame number as pixel [0, 0]
}

def setup_camera():
    try:
        from camera.lucamcamera import LucamCamera

        width, height = camera_parameters['total_width'], camera_parameters['total_height'] # 490 * 390 um
        ROI_width = camera_parameters['ROI_width']
        ROI_height = camera_parameters['ROI_height']
        x = int(width / 2 - ROI_width / 2)
        y = int(height / 2 - ROI_height / 2)

        camera = LucamCamera(trigger=True, exposure=camera_parameters['exposure'],
                             gain=camera_parameters['gain'],
                             binning=camera_parameters['binning'],
                             x=x, y=y, width=ROI_width, height=ROI_height, depth=camera_parameters['depth'])

    except ImportError:
        warnings.warn('Cannot import Lucam - using a fake camera object')
        from camera import FakeCamera
        camera = FakeCamera()

    camera_parameters['pixel_width'] = camera_parameters['pixel_width']*camera_parameters['binning']
    camera.camera_parameters = camera_parameters

    return camera
