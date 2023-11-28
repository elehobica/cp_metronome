# Metronome for Circuit Playground Express

## Overview
Metronome for Circuit Playground Express by CircuitPython

This project features:
* Adjustable Tempo (30 ~ 252 bpm)
* Adjustable Beat (1/4, 2/4, 3/4, 4/4, ... 10/4)
* Tempo/Beat sound by built-in speaker
* Tempo/Beat display by NeoPixel
* Start / Stop by tap
* Tempo/Beat settings stored

## Supported Board
* Circuit Playground Express

## Programming Environment
* CircuitPython 8.2.8 [https://circuitpython.org/board/circuitplayground_express/](https://circuitpython.org/board/circuitplayground_express/)

## Control Guide
* Metronome is in stop state when power on
* Double tap to start metronome, double tap again to stop metronome
* With slide switch ON (left), push A button for tempo down, push B button for tempo up
* With slide switch OFF (right), push A button for decrease beat, push B button for increase beat
* Setting will be stored in Flash storage when stopping metronome (Note that this works only in standalone mode, doesn't work with terminal debug mode)
