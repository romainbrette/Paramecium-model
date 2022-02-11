from __future__ import print_function
'''
A camera using Lucam
'''
import collections
import os
import sys
import threading
import warnings
from time import sleep, time
import PIL
import imageio
from .lucam import Lucam, API, LucamError

__all__ = ['LucamCamera']

class FileWriteThread(threading.Thread):
    def __init__(self, *args, **kwds):
        self.queue = kwds.pop('queue')
        threading.Thread.__init__(self, *args, **kwds)
        self.running = True

    def run(self):
        self.running = True
        while self.running:
            # wait until something is in the queue
            try:
                fname, frame_number, elapsed_time, frame = self.queue.popleft()
                if fname is None:
                    # special marker for the end of recording
                    break
                imageio.imwrite(fname, frame)
                if frame_number % 20 == 0:
                    print('Finished writing {}.'.format(fname))
            except IndexError:
                # queue is emtpy, wait
                sleep(0.01)
                # TODO: Store image metadata to file as well?

class AcquisitionThread(threading.Thread):
    def __init__(self, *args, **kwds):
        if any(kwd not in kwds for kwd in ['record_time', 'directory',
                                           'file_prefix', 'camera']):
            raise ValueError('Need to provide "n_images", "record_time",'
                             '"directory", "file_prefix", and "camera" keyword'
                             'arguments')
        self.record_time = kwds.pop('record_time')
        self.directory = kwds.pop('directory')
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.file_prefix = kwds.pop('file_prefix')
        self.camera = kwds.pop('camera')
        self.queue = kwds.pop('queue')
        self.frame_debug = kwds.pop('frame_debug', False)
        kwds['name'] = 'image_acquire_thread'
        self.running = True
        self.delay = kwds.pop('delay', 0.)
        self.nimages = kwds.pop('nimages')

        threading.Thread.__init__(self, *args, **kwds)

    def run(self):
        self.running = True

        sleep(self.delay)
        elapsed_time = 0.0
        n = 0
        t0 = time()
        frame = self.camera.frame
        try:
            # might time out if no HW trigger
            while (elapsed_time < self.record_time*1000) and self.running and n < self.nimages:
                frame = self.camera.TakeFastFrame()
                n +=1
                elapsed_time = time()-t0
                image_fname = os.path.join(self.directory,
                                           '{}{:05d}.tiff'.format(self.file_prefix,
                                                                    n))
                if self.frame_debug:
                    # Put the frame number into pixel [0, 0] for debugging
                    # Note that e.g. for dtype uint8, this means the frame
                    # number starts again at 0 after passing 255
                    frame[0, 0] = n
                # Put image into queue for disk storage
                self.queue.append((image_fname, n, elapsed_time, frame))
        except LucamError:
            print('TakeFastFrame() timed out')
        # Put the end marker into the queue
        self.queue.append((None, None, None, None))
        if self.nimages is not None:
            print('Got {}/{} images'.format(n,self.nimages))


class LucamCamera(object):
    def __init__(self, exposure=None, gain=None, binning=1, x=0, y=0, width=None, height=None, trigger=False, depth = 8):
        self.acquisition_thread = None
        self.file_thread = None
        self.camera_parameters = None  # assigned in setup_camera
        self.cam = Lucam()
        self.cam.CameraReset()

        self.exposure=exposure
        self.gain=gain

        default = self.cam._default_frameformat
        if width is None:
            width = default.width
        if height is None:
            height = default.height
        if depth == 16:
            depth = API.LUCAM_PF_16
        elif depth == 8:
            depth = API.LUCAM_PF_8

        self.cam.SetFormat(
        Lucam.FrameFormat(int(x*1. / (16 * binning))* 16 * binning,
                              int(y * 1. / (16 * binning)) * 16 * binning,
                              int(width*1. / (16 * binning)) * 16 * binning,
                              int(height*1. / (16 * binning)) * 16 * binning,
                              depth, # API.LUCAM_PF_8,
                              binningX=binning, binningY=binning),
            framerate=100.0)
        frameformat, framerate = self.cam.GetFormat()
        print("Frame rate: {} Hz".format(framerate))

        snapshot = self.cam.default_snapshot()
        snapshot.exposure = exposure
        snapshot.gain = gain
        snapshot.format = frameformat
        #snapshot = Lucam.Snapshot(exposure=exposure, gain=gain, exposureDelay=0.,
        #                          timeout=1000.0, format=frameformat)
        self.cam.frame = self.cam.TakeSnapshot()
        self.cam.EnableFastFrames(snapshot)
        if trigger:
            self.cam.SetTriggerMode(True)
            self.cam.SetTimeout(True, 1000.0)  # timeout after 1 s

        #if exposure is not None:
        #    self.cam.set_properties(exposure=exposure)
        #if gain is not None:
        #    self.cam.set_properties(gain=gain)
        # lucam.SetFormat(
        #     Lucam.FrameFormat(0, 0, 688 * 4, 548 * 4, API.LUCAM_PF_16,
        #                       binningX=4, flagsX=1, binningY=4, flagsY=1),
        #     framerate=100.0)

    def __del__(self):
        try:
            self.cam.DisableFastFrames()
            self.cam.CameraClose()
            del self.cam
        except Exception:
            pass

    def record_sequence(self, record_time, directory, file_prefix='', delay=0., nimages=None):
        '''
        Starts the acquisition of a sequence of frames and writes them to
        disk continuously (using a thread). After acquisition of all images,
        writes a meta data file with the exposure times.

        Parameters
        ----------
        record_time : float
            Total recording time in seconds
        directory : str
            Name of the target directory (will be created if it does not exist)
        file_prefix : str
            Will be added to the filename, e.g. image 3 for
            ``file_prefix`` = ``'trial_1``: "image_trial_1_003.png"
        '''
        queue = collections.deque()
        self.file_thread = FileWriteThread(queue=queue)
        frame_debug = self.camera_parameters['frame_debug']
        self.acquisition_thread = AcquisitionThread(record_time=record_time,
                                                    camera=self.cam,
                                                    directory=directory,
                                                    file_prefix=file_prefix,
                                                    queue=queue, delay=delay,
                                                    nimages=nimages,
                                                    frame_debug=frame_debug)
        self.file_thread.start()
        self.acquisition_thread.start()

    def stop(self):
        '''
        Terminate acquisition
        '''
        self.acquisition_thread.running = False
        self.file_thread.running = False
        self.acquisition_thread.join()
        self.file_thread.join()

    def wait_until_finished(self):
        '''
        Waits until acquisition has finished
        '''
        self.acquisition_thread.join()
        self.file_thread.join()
