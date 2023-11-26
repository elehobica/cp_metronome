import time
import board
import pwmio
from adafruit_circuitplayground import cp

cp.pixels.brightness = 0.2

piezo = pwmio.PWMOut(board.A2, duty_cycle=0, frequency=440, variable_frequency=True)
freq = 1397

count = 0
while True:
    piezo.duty_cycle = 65535 // 2  # On 50%
    if count % 4 == 0:
        cp.pixels.fill((0, 50, 0))
        piezo.frequency = freq * 2
    else:
        cp.pixels.fill((50, 0, 0))
        piezo.frequency = freq
    time.sleep(0.05)
    cp.pixels.fill((0, 0, 0))
    time.sleep(0.05)
    piezo.duty_cycle = 0  # Off
    time.sleep(0.6)
    count += 1