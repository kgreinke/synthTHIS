# ***************************************************************************
#   * Program:  synthTHIS.py
#   * Purpose:  Synthesizer implementation in python
#   * Author:   Kat Greinke
#   * Date:     Today
#   * Class:    CS410P Music, Sound, and Computers
# ***************************************************************************

import numpy as np
import sounddevice as sd
import soundfile as sf
import pygame.midi as midi
import time
from scipy.io import wavfile
from scipy import signal

#midi startup
midi.init()
default_id = midi.get_default_input_id()
midi_input = midi.Input(device_id = default_id)

#globals
osc_type = 'sine'           #defaults to sine but can be changes to square or saw
log = False
attack = 0.020
release = 0.1
sample_clock = 0
sample_rate = 48000
block_size = 16
buffer_size = 256
out_keys = dict()


# ***************************************************************************
# Simple record function that allows a user to record audio into a wav file
# ***************************************************************************
def record_mode():
    filename = 'default.wav'
    filename = input("Enter a name for your wav file in the form 'name.wav': ")
    input("To exit record mode, press Ctrl+C\nHit enter once ready...")
    
    try:
        output = blank_function()
        wavfile.write(filename, sample_rate, output.astype(np.int16))
    except KeyboardInterrupt:
        print("Recording finished!")


# *********************************************************************************************
#   * Class:            Note
#   * Purpose:          Simple class to hold individual note data all in one object
#   * Data Members:     frequency           -> holds an integer for the note's frequency
#                       osc_type            -> holds the type of oscillator used for the note
#                                               'sine' for a sin oscillator
#                                               'square' for a square oscillator
#                                               'saw' for a saw oscillator
#                       playing             -> boolean representing if a note is on or off
#                                               False for off
#                                               True for on
#                       attack_remaining    -> integer representing time in seconds of
#                                              the remaining attack for this note
#                       release_remaining   -> integer representing time in seconds of
#                                              the remaining release time for this note
# **********************************************************************************************
class Note:
    def __init__(self, key, osc):
        self.frequency = key_to_frequency(key)
        self.osc_type = osc
        self.playing = True
        self.attack_remaining = attack
        self.release_remaining = None

    def release(self):
        self.release_remaining = release

    def samples(self, linespace):