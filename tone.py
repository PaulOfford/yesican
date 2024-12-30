import pysine
from time import sleep

length = 0.1
delay = 0.3
frequencies = [293, 329, 369, 392, 440, 493]

for freq in frequencies:
    pysine.sine(frequency=freq, duration=length)
    sleep(delay)
