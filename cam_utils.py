import numpy as np
import time

import magpyx
from magpyx.utils import ImageStream

import purepyindi
from purepyindi import INDIClient

class CAM:
    def __init__(self, channel):
        self.channel = channel
        self.cam_stream = ImageStream(channel)
        self.Nframes = 10

    def set_roi(self, xc, yc, npix, client, delay=0.25):
        client.wait_for_properties(
            [f'{self.channel}.roi_region_x', f'{self.channel}.roi_region_y', 
             f'{self.channel}.roi_region_h', f'{self.channel}.roi_region_w', 
             f'{self.channel}.roi_set']
        )
        client[f'{self.channel}.roi_region_x.target'] = xc
        client[f'{self.channel}.roi_region_y.target'] = yc
        client[f'{self.channel}.roi_region_h.target'] = npix
        client[f'{self.channel}.roi_region_w.target'] = npix
        time.sleep(delay)
        client[f'{self.channel}.roi_set.request'] = purepyindi.SwitchState.ON
        time.sleep(delay)

    def set_exptime(self, exptime, client, delay=0.25):
        client.wait_for_properties([f'{self.channel}.exptime',])
        client[f'{self.channel}.exptime.target'] = exptime

    def snap(self):
        im = np.sum(np.array(self.cam_stream.grab_many(self.Nframes)), axis=0)/self.Nframes
        return im
    
    def snap_cube(self):
        ims = np.array(self.cam_stream.grab_many(self.Nframes))
        return ims


