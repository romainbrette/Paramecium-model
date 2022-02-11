'''
Experiment with current pulses.
'''
from __future__ import print_function
from clampy import *
#from .utils import *
from init_rig import *
import utils
import current_pulses_analysis
from numpy.random import shuffle
from os.path import join

default_parameters = dict(
    name = 'current pulses',
    ntrials = 10,
    start = 300*ms,
    end = 400*ms,
    total_duration = 1.4*second,
    I_min = -1*nA,
    I_max = 4*nA,
    video_lag = 2*ms, # ms after pulse start
    framerate = None, # ex: 90/second
    dt = dt,
    notes = '''A series of current pulses with varying amplitudes are injected through Ic2. \
    Amplitudes are linearly arranged, from the largest positive one \
    to the largest negative one. This is because the largest negative currents tend to change the resting potential. \
    Simultaneously, images are taken by a camera using a trigger synchronized to the recording.'''
)

def do_the_experiment(analysis=True, camera=None, path=None, display=True, **parameters):
    print('* Current pulse experiment *')

    # Get parameters
    P = dict(default_parameters)
    P.update(parameters)
    start, end, total_duration = P['start'], P['end'], P['total_duration']

    # Current amplitudes
    P['amplitudes'] = linspace(P['I_min'], P['I_max'], P['ntrials'])[::-1]
    # shuffle(amplitudes)

    path, data_path, image_path = utils.prepare_experiment(path, camera, P)

    # Camera trigger
    if camera is not None:
        trigger = ticks(total_duration,dt,P['framerate'], t0=start+P['video_lag'])
        utils.preliminary_video(camera, path, trigger, board)
    else:
        trigger = None

    # Run the experiment
    board.reset_clock()
    for i, ampli in enumerate(P['amplitudes']):
        print('Amplitude ',ampli)
        if camera is not None:
            # Start camera
            camera.record_sequence(total_duration + 500 * ms,
                                   join(image_path, '{:03d}'.format(i)),
                                   nimages=sum(trigger))

        Ic = steps([(0*nA, start),
                    (ampli, end),
                    (0*nA, total_duration)], dt)
        board.acquire('V1', 'V2', Ic2=Ic, trigger=trigger, save=join(data_path, 'data{:03d}.txt.gz'.format(i)))

        if camera is not None:
            camera.stop()

    # Plot
    if analysis:
        current_pulses_analysis.do_analysis(path, display=display)

if __name__ == '__main__':
    do_the_experiment(analysis=True, display=True)
    # With camera:
    #from .setup_camera import setup_camera
    #do_the_experiment(analysis=True, camera=setup_camera(), framerate=30/second)

