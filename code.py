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

FREQ = 1397
TEMPO_MIN = 30
TEMPO_MAX = 252
TEMPO_DEFAULT = 86  # Moderato
BEAT_DEFAULT = 4
CONFIG_FILE = './config.txt'

bt_a_accum = 0
bt_b_accum = 0
button_last = 50
tempo = TEMPO_DEFAULT
beat = BEAT_DEFAULT
tempo_inc = 1
tempo_show = 0
beat_show = 0

def reorder_pixel(i):
    return 4 - (i % 5) + (i // 5) * 5  # reorder 4, 3, 2, 1, 0, 9, 8, 7, 6, 5

def neo_pixel_show_point(color, point):
    for i in range(10):
        if i == point:
            cp.pixels[reorder_pixel(i)] = color
        else:
            cp.pixels[reorder_pixel(i)] = (0, 0, 0)

def neo_pixel_show_odd(color):
    for i in range(10):
        if i % 2 == 0:
            cp.pixels[reorder_pixel(i)] = (0, 0, 0)
        else:
            cp.pixels[reorder_pixel(i)] = color

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
    global tempo, beat
    try:
        for line in open(CONFIG_FILE, 'r'):
            if 'tempo=' in line:
                tempo = int(line.split('=')[1])
            if 'beat=' in line:
                beat = int(line.split('=')[1])
    except OSError:
        print(f'"{CONFIG_FILE}" not found.')

def save_config(tempo, beat):
    try:
        storage.remount('/', False)  # Read-only: False
        with open(CONFIG_FILE, 'w') as f:
            f.write(f'{tempo=}\n')
            f.write(f'{beat=}\n')
        storage.remount('/', True)  # Read-only: False
    except RuntimeError:
        print(f'cannot save to {CONFIG_FILE}')

def check_button_status(dec_show = False):
    global bt_a_accum, bt_b_accum
    global button_last
    global tempo, beat
    global tempo_show, beat_show
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
        if button_last < 50:
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
            if dec_show and tempo_show > 0:
                tempo_show -= 1
            tempo_inc = 1
    else:  # BEAT selection
        if button_last < 50:
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
            if dec_show and beat_show > 0:
                beat_show -= 1
    if bt_a or bt_b:
        button_last = 0
    else:
        button_last += 1

def main():
    cp.pixels.brightness = 0.2

    cp.detect_taps = 2  # double tap for enable/disable sound

    load_config()

    count = 0
    enable = False

    while True:
        # Start time
        t = time.monotonic()

        check_button_status(dec_show = True)

        if cp.tapped:
            enable = not enable
            if not enable:
                save_config(tempo, beat)

        # Show configuration
        if tempo_show >= 9:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
        elif tempo_show == 8:
            neo_pixel_show_point((0, 25, 25), (tempo // 100) % 10)
        elif tempo_show == 7:
            neo_pixel_show_point((0, 25, 25), (tempo // 100) % 10)
        elif tempo_show == 6:
            if tempo < 100:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
            else:
                neo_pixel_show_point((0, 25, 25), -1)
        elif tempo_show == 5:
            neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
        elif tempo_show == 4:
            if tempo < 60:
                neo_pixel_show_level((0, 0, 50), get_tempo_level(tempo))
            else:
                neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
        elif tempo_show == 3:
            if tempo < 60:
                neo_pixel_show_point((0, 25, 25), (tempo // 10) % 10)
            else:
                neo_pixel_show_point((0, 25, 25), -1)
        elif tempo_show == 2:
            if tempo < 60:
                neo_pixel_show_point((0, 25, 25), -1)
            else:
                neo_pixel_show_point((0, 25, 25), tempo % 10)
        elif tempo_show == 1:
            neo_pixel_show_point((0, 25, 25), tempo % 10)
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
        while t_rest > 0.12:
            time.sleep(0.1)
            check_button_status()
            t_rest = 60 / tempo - (time.monotonic() - t)
        if t_rest > 0:
            time.sleep(t_rest)

if __name__ == '__main__':
    main()
