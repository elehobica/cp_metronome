# cp_metronome
# ------------------------------------------------------
# Copyright (c) 2023, Elehobica
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# As for the libraries which are used in this software, they can have
# different license policies, look at the subdirectories of lib directory.
# ------------------------------------------------------

import time
import storage
from adafruit_circuitplayground import cp

# default setting parameters
FREQ = 1397
TEMPO_MIN = 30
TEMPO_MAX = 252
TEMPO_DEFAULT = 86  # Moderato
BEAT_DEFAULT = 4
CONFIG_FILE = './config.txt'

# global variables
bt_a_accum = 0
bt_b_accum = 0
button_last = 100
tempo_inc = 1

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

def check_button_status(tempo, beat, tempo_show, beat_show, decr = False):
    global bt_a_accum, bt_b_accum
    global button_last
    global tempo_inc

    # Get button status
    bt_a = cp.button_a
    bt_b = cp.button_b and not bt_a
    if bt_a:
        bt_a_accum += 1
    elif bt_b:
        bt_b_accum += 1
    else:
        bt_a_accum = 0
        bt_b_accum = 0
    if cp.switch:  # TEMPO adjust
        if button_last < 100:
            if bt_a_accum == 1 or (bt_a_accum >= 5 and bt_a_accum % 5 == 0):
                if tempo - tempo_inc > TEMPO_MIN:
                    tempo -= tempo_inc
                    tempo_inc += 1
                else:
                    tempo = TEMPO_MIN
            if bt_b_accum == 1 or (bt_b_accum >= 5 and bt_b_accum % 5 == 0):
                if tempo + tempo_inc < TEMPO_MAX:
                    tempo += tempo_inc
                    tempo_inc += 1
                else:
                    tempo = TEMPO_MAX
        beat_show = 0
        if bt_a or bt_b:
            tempo_show = 4 if tempo < 60 else 6 if tempo < 100 else 9
        else:
            if decr and tempo_show > 0:
                tempo_show -= 1
            tempo_inc = 1
    else:  # BEAT selection
        if button_last < 100:
            if bt_a_accum == 1 or (bt_a_accum >= 10 and bt_a_accum % 10 == 0):
                if beat > 1:
                    beat -= 1
            if bt_b_accum == 1 or (bt_b_accum >= 10 and bt_b_accum % 10 == 0):
                if beat < 10:
                    beat += 1
        tempo_show = 0
        if bt_a or bt_b:
            beat_show = 3
        else:
            if decr and beat_show > 0:
                beat_show -= 1
    if bt_a or bt_b:
        button_last = 0
    else:
        button_last += 1
    return tempo, beat, tempo_show, beat_show

def show_settings(tempo, beat, tempo_show, beat_show, enable, count):
    if tempo_show > 0:
        if tempo < 60:
            if tempo_show >= 4:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
            elif tempo_show == 3:
                neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
            elif tempo_show == 2:
                neo_pixel_show_point((0, 25, 25), -1)
            else:
                neo_pixel_show_point((0, 25, 25), tempo % 10)
        elif tempo < 100:
            if tempo_show >= 6:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
            elif tempo_show >= 4:
                neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
            elif tempo_show == 3:
                neo_pixel_show_point((0, 25, 25), -1)
            else:
                neo_pixel_show_point((0, 25, 25), tempo % 10)
        else:
            if tempo_show >= 9:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
            elif tempo_show >= 7:
                neo_pixel_show_point((0, 25, 25), (tempo // 100) % 10)
            elif tempo_show == 6:
                neo_pixel_show_point((0, 25, 25), -1)
            elif tempo_show >= 4:
                neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
            elif tempo_show == 3:
                neo_pixel_show_point((0, 25, 25), -1)
            else:
                neo_pixel_show_point((0, 25, 25), tempo % 10)
    elif beat_show > 0:
        neo_pixel_show_level((50, 50, 0), beat)
    elif not enable:
        neo_pixel_show_point((10, 10, 10), count % 10)

def main():
    cp.pixels.brightness = 0.2

    cp.detect_taps = 2  # double tap for enable/disable sound

    tempo, beat = load_config()
    tempo_show = 0
    beat_show = 0
    count = 0
    enable = False

    while True:
        # Start time
        t = time.monotonic()

        # Show settings by NeoPixel
        show_settings(tempo, beat, tempo_show, beat_show, enable, count)

        tempo, beat, tempo_show, beat_show = check_button_status(tempo, beat, tempo_show, beat_show, decr = True)

        if cp.tapped:
            enable = not enable
            if not enable:
                save_config(tempo, beat)

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
            cp.stop_tone()

        count += 1
        # Set interval depending on tempo
        t_rest = 60 / tempo - (time.monotonic() - t)
        while t_rest > 0.12:
            time.sleep(0.1)
            tempo, beat, tempo_show, beat_show = check_button_status(tempo, beat, tempo_show, beat_show)
            t_rest = 60 / tempo - (time.monotonic() - t)
        if t_rest > 0:
            time.sleep(t_rest)

if __name__ == '__main__':
    main()
