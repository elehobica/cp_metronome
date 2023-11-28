import time
import storage
from adafruit_circuitplayground import cp

FREQ = 1397
TEMPO_MIN = 30
TEMPO_MAX = 252
TEMPO_DEFAULT = 86  # Moderato
BEAT_DEFAULT = 4
CONFIG_FILE = './config.txt'

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

def get_tempo_level(tempo):
    lut = (40, 60, 70, 80, 90, 100, 110, 120, 140, 160)
    for i, value in enumerate(lut):
        if tempo < value:
            return i
    else:
        return len(lut)

def load_config():
    tempo = TEMPO_DEFAULT
    beat = BEAT_DEFAULT
    try:
        for line in open(CONFIG_FILE, 'r'):
            if 'tempo=' in line:
                tempo = int(line.split('=')[1])
            if 'beat=' in line:
                beat = int(line.split('=')[1])
    except OSError:
        print(f'"{CONFIG_FILE}" not found.')
    return tempo, beat

def save_config(tempo, beat):
    try:
        storage.remount('/', False)  # Read-only: False
        with open(CONFIG_FILE, 'w') as f:
            f.write(f'{tempo=}\n')
            f.write(f'{beat=}\n')
        storage.remount('/', True)  # Read-only: False
    except RuntimeError:
        print(f'cannot save to {CONFIG_FILE}')

def main():
    cp.pixels.brightness = 0.2

    cp.detect_taps = 2  # double tap for enable/disable sound

    tempo, beat = load_config()

    count = 0
    tempo_inc = 1
    tempo_show = 0
    beat_show = 0
    enable = False

    while True:
        # Start time
        t = time.monotonic()

        # Get button status
        bt_a = cp.button_a
        bt_b = cp.button_b and not bt_a
        if cp.switch:  # TEMPO adjust
            beat_show = 0
            if not bt_a and not bt_b:
                tempo_inc = 1
                if tempo_show > 0:
                    tempo_show -= 1
            else:
                tempo_show = 3
            if bt_a:
                if tempo - tempo_inc > TEMPO_MIN:
                    tempo -= tempo_inc
                    tempo_inc += 1
                else:
                    tempo = TEMPO_MIN
            if bt_b:
                if tempo + tempo_inc < TEMPO_MAX:
                    tempo += tempo_inc
                    tempo_inc += 1
                else:
                    tempo = TEMPO_MAX
        else:  # BEAT selection
            tempo_show = 0
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
            if not enable:
                save_config(tempo, beat)

        # Show configuration
        if tempo_show > 0:
            neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
        elif beat_show > 0:
            neo_pixel_show_level((50, 50, 0), beat)

        if enable:
            # Metronome Light & Sound
            if count % beat == 0:
                cp.start_tone(FREQ * 2)
                if tempo_show == 0 and beat_show == 0:
                    cp.pixels.fill((0, 50, 0))
            else:
                cp.start_tone(FREQ)
                if tempo_show == 0 and beat_show == 0:
                    cp.pixels.fill((50, 0, 0))
            time.sleep(0.05)
            cp.stop_tone()
            if tempo_show == 0 and beat_show == 0:
                cp.pixels.fill((0, 0, 0))
            time.sleep(0.05)
        else:
            if tempo_show == 0 and beat_show == 0:
                neo_pixel_show_point((10, 10, 10), count % 10)
            cp.stop_tone()

        count += 1
        # Set interval depending on tempo
        t_rest = 60 / tempo - (time.monotonic() - t)
        if t_rest > 0:
            time.sleep(t_rest)

if __name__ == '__main__':
    main()
