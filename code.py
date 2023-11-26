import time
import board
import pwmio
from adafruit_circuitplayground import cp

cp.pixels.brightness = 0.2

piezo = pwmio.PWMOut(board.A2, duty_cycle=0, frequency=440, variable_frequency=True)
freq = 1397

count = 0
inc = 1
bpm = 86  # Moderato
bpm_show = 0
beat = 4
beat_show = 0

while True:
    # Start time
    t = time.monotonic()

    # Get button status
    bt_a = cp.button_a
    bt_b = cp.button_b and not bt_a
    if cp.switch:
        beat_show = 0
        if not bt_a and not bt_b:
            inc = 1
            if bpm_show > 0:
                bpm_show -= 1
        else:
            bpm_show = 3
        if bt_a:
            if bpm - inc > 30:
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
    else:
        bpm_show = 0
        if not bt_a and not bt_b:
            if beat_show > 0:
                beat_show -= 1
        else:
            beat_show = 3
        if bt_a:
            if beat > 1:
                beat -= 1
        if bt_b:
            if beat < 10:
                beat += 1

    # bpm level
    if bpm_show > 0:
        if bpm < 40:
            level = 0
        elif bpm < 60:
            level = 1
        elif bpm < 70:
            level = 2
        elif bpm < 80:
            level = 3
        elif bpm < 90:
            level = 4
        elif bpm < 100:
            level = 5
        elif bpm < 110:
            level = 6
        elif bpm < 120:
            level = 7
        elif bpm < 140:
            level = 8
        elif bpm < 160:
            level = 9
        else:
            level = 10
        for i in range(level):
            j = 4 - (i % 5) + (i // 5) * 5 # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5
            cp.pixels[j] = (0, 0, 50)
        for i in range(level, 10):
            j = 4 - (i % 5) + (i // 5) * 5 # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5
            cp.pixels[j] = (0, 0, 0)
    elif beat_show > 0:
        for i in range(beat):
            j = 4 - (i % 5) + (i // 5) * 5 # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5
            cp.pixels[j] = (50, 50, 0)
        for i in range(beat, 10):
            j = 4 - (i % 5) + (i // 5) * 5 # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5
            cp.pixels[j] = (0, 0, 0)

    # Metronome Light & Sound
    piezo.duty_cycle = 65535 // 2  # On 50%
    if count % beat == 0:
        if bpm_show == 0 and beat_show == 0:
            cp.pixels.fill((0, 50, 0))
        piezo.frequency = freq * 2
    else:
        if bpm_show == 0 and beat_show == 0:
            cp.pixels.fill((50, 0, 0))
        piezo.frequency = freq
    time.sleep(0.05)
    if bpm_show == 0 and beat_show == 0:
        cp.pixels.fill((0, 0, 0))
    time.sleep(0.05)
    piezo.duty_cycle = 0  # OFF

    count += 1
    # Set interval depending on bpm
    time.sleep(60 / bpm - (time.monotonic() - t))
