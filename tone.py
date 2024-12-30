# import pysine
# from time import sleep
#
# length = 0.1
# delay = 0.3
# frequencies = [293, 329, 369, 392, 440, 493]
#
# for freq in frequencies:
#     pysine.sine(frequency=freq, duration=length)
#     sleep(delay)
#
# #!/usr/bin/env python3

import pygame
from array import (array)
from pygame.mixer import (Sound, get_init, pre_init)

class BrakeTone(Sound):
    active = True
    duration = 80

    def __init__(self, frequency=0, volume=0.5):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def __call__(self):
        if self.active:
            self.play(self.duration)
        return self

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < (period / 2):
                samples[time] = +amplitude
            else:
                samples[time] = -amplitude
        return samples

if __name__ == "__main__":
    from time import sleep
    pre_init(44100, -16, 1, 1024)
    pygame.init()
    for n in range(0, 10):
        BrakeTone(frequency=440, volume=0.5)()
        sleep(0.2)
