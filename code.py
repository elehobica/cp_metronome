import time
import board
import pwmio
from adafruit_circuitplayground import cp

cp.pixels.brightness = 0.2

piezo = pwmio.PWMOut(board.A2, duty_cycle=0, frequency=440, variable_frequency=True)
freq = 1397

count = 0
bpm = 120
inc = 1

while True:
    # Start time
    t = time.monotonic()

    # Get button status
    bt_a = cp.button_a
    bt_b = cp.button_b and not bt_a
    if not bt_a and not bt_b:
        inc = 1

    # Light & Sound
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
    piezo.duty_cycle = 0  # OFF

    # Button I/F
    if bt_a:
        if bpm - inc> 30:
            bpm -= inc
            inc += 1
        else:
            bpm = 30
    if bt_b:
        if bpm + inc < 252:
            bpm += inc
            inc += 1
        else:
            bpm = 252
    count += 1

    # Set interval depending on bpm
    time.sleep(60 / bpm - (time.monotonic() - t))
