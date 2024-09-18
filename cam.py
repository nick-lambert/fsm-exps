import numpy as np

import magpyx
from magpyx.utils import ImageStream

class CAM:
    def __init__(channel):
        self.cam_stream = ImageStream('channel')
        self.Nframes = 10

    def snap(self):
        im = self.cam_stream.grab_many(self.Nframes)/self.Nframes
        return im
    
    def snap_cube(self):
        ims = self.grab_many(self.Nframes)
        return ims


