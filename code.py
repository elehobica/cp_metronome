import time
from adafruit_circuitplayground import cp

FREQ = 1397
BPM_MIN = 30
BPM_MAX = 252
BPM_DEFAULT = 86  # Moderato
BEAT_DEFAULT = 4

def reorder_pixel(i):
    return 4 - (i % 5) + (i // 5) * 5  # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5

def neo_pixel_show_point(color, point):
    for i in range(10):
        if i == point:
            cp.pixels[reorder_pixel(i)] = color
        else:
            cp.pixels[reorder_pixel(i)] = (0, 0, 0)

def neo_pixel_show_level(color, level):
    for i in range(level):
        cp.pixels[reorder_pixel(i)] = color
    for i in range(level, 10):
        cp.pixels[reorder_pixel(i)] = (0, 0, 0)

def get_bpm_level(bpm):
    lut = (40, 60, 70, 80, 90, 100, 110, 120, 140, 160)
    for i, value in enumerate(lut):
        if bpm < value:
            return i
    else:
        return len(lut)

def main(bpm, beat):
    cp.pixels.brightness = 0.2

    cp.detect_taps = 2  # double tap for enable/disable sound

    count = 0
    inc = 1
    bpm_show = 0
    beat_show = 0
    enable = False

    while True:
        # Start time
        t = time.monotonic()

        # Get button status
        bt_a = cp.button_a
        bt_b = cp.button_b and not bt_a
        if cp.switch:  # BPM adjust
            beat_show = 0
            if not bt_a and not bt_b:
                inc = 1
                if bpm_show > 0:
                    bpm_show -= 1
            else:
                bpm_show = 3
            if bt_a:
                if bpm - inc > BPM_MIN:
                    bpm -= inc
                    inc += 1
                else:
                    bpm = BPM_MIN
            if bt_b:
                if bpm + inc < BPM_MAX:
                    bpm += inc
                    inc += 1
                else:
                    bpm = BPM_MAX
        else:  # BEAT selection
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

        if cp.tapped:
            enable = not enable

        # Show configuration
        if bpm_show > 0:
            neo_pixel_show_level((0, 0, 50), get_bpm_level(bpm))
        elif beat_show > 0:
            neo_pixel_show_level((50, 50, 0), beat)

        if enable:
            # Metronome Light & Sound
            if count % beat == 0:
                cp.start_tone(FREQ * 2)
                if bpm_show == 0 and beat_show == 0:
                    cp.pixels.fill((0, 50, 0))
            else:
                cp.start_tone(FREQ)
                if bpm_show == 0 and beat_show == 0:
                    cp.pixels.fill((50, 0, 0))
            time.sleep(0.05)
            cp.stop_tone()
            if bpm_show == 0 and beat_show == 0:
                cp.pixels.fill((0, 0, 0))
            time.sleep(0.05)
        else:
            if bpm_show == 0 and beat_show == 0:
                neo_pixel_show_point((10, 10, 10), count % 10)
            cp.stop_tone()

        count += 1
        # Set interval depending on bpm
        t_rest = 60 / bpm - (time.monotonic() - t)
        if t_rest > 0:
            time.sleep(t_rest)

if __name__ == '__main__':
    main(BPM_DEFAULT, BEAT_DEFAULT)
