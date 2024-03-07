# ****************************************************
#   * Program:  synthTHIS.py
#   * Purpose:  Synthesizer implementation in python
#   * Author:   Kat Greinke
#   * Date:     Today
#   * Class:    CS410P Music, Sound, and Computers
# ****************************************************

import numpy as np
import sounddevice as sd
import soundfile as sf
import pygame.midi as midi
import time
from scipy.io import wavfile
from scipy import signal

# -- START - "globals" --

# osc_type                  -> string holding which oscillator type is currently being
#                              used by the synthesizer
#                           -> default - sine
#                           -> options: sine, saw, square
osc_type = 'sine'

# log                       -> represents if verbose mode is activated
#                           -> default - False
#                           -> options: True, False
log = False                 

# attack                    -> float holding the attack time for note synthesis
#                           -> default - 0.020
attack = 0.020

# release                   -> float holding the release time for note synthesis
#                           -> default - 0.10
release = 0.10

# sample_clock              -> tracker of samples output to ensure correctly phased waveforms
#                           -> default - none
sample_clock = 0

# sample_rate               -> integer holding the sample rate in sps for audio output
#                           -> default - 48000
#                           -> options - 44100, 48000
sample_rate = 48000

# block_size                -> samples to process, higher values help with slower computers
#                           -> default - 16
block_size = 16

# out_keys                  -> dynamic dictionary of currently playing keys 
#                           -> index by MIDI key number 
out_keys = dict()

# midi_dev                  -> holds device info for event processing
midi_dev = None

# -- END - "globals" --


# -- midi startup --
midi.init()
default_id = midi.get_default_input_id()
midi_input = midi.Input(device_id = default_id)
count = midi.get_count()
if log:
    print(f"{count} midi devices found")
for i in range(count):
    midi_dev = midi.get_device_info(i)
    if log:    
        print("%s name: %s input: %s opened: %s" % (midi_dev))
    if midi_name in midi_dev[1].decode() and midi_dev[2]:
        device = i
if device:
    if log:
        print(f"Setting device to {device}")
    midi_dev = midi.Input(device)
else:
    print("Error: midi device undefined!")


# *********************************************************************************************
# Purpose:      Sine wave generator. 
# Parameters:   frequency   -> holds an integer representation of the frequency requested
#               time        -> holds an integer representation of the time requested'
# Returns:      wave        -> numpy array holding a sine wave
# *********************************************************************************************
def sine_wave(frequency, time):
    wave = np.sin(2 * np.pi * frequency * time)
    return wave

# *********************************************************************************************
# Purpose:      Saw wave generator. 
# Parameters:   frequency   -> holds an integer representation of the frequency requested
#               time        -> holds an integer representation of the time requested'
# Returns:      wave        -> numpy array holding a saw wave
# *********************************************************************************************
def saw_wave(frequency, time):
    wave = (frequency * time) % 2.0 - 1.0
    return wave

# *********************************************************************************************
# Purpose:      Square wave generator. 
# Parameters:   frequency   -> holds an integer representation of the frequency requested
#               time        -> holds an integer representation of the time requested'
# Returns:      wave        -> numpy array holding a square wave
# *********************************************************************************************
def square_wave(frequency, time):
    wave = np.sign((frequency * time) % 2.0 - 1.0)
    return wave


# **********************************************************************************************
# Simple record function that allows a user to record audio into a wav file
# **********************************************************************************************
def record_mode():
    filename = 'default.wav'
    filename = input("Enter a name for your wav file in the form 'name.wav': ")
    input("To exit record mode, press Ctrl+C\nHit enter once ready...")
    
    try:
        output = blank_function()
        wavfile.write(filename, sample_rate, output.astype(np.int16))
    except KeyboardInterrupt:
        print("Recording finished!")


# **********************************************************************************************
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
    # ******************************************************************************************
    # Purpose:          Note default constructor
    # Parameters:       self        -> object being created
    #                   key         -> object
    # ******************************************************************************************
    def __init__(self, key, osc):
        self.frequency = key_to_frequency(key)
        self.osc_type = osc
        self.playing = True
        self.attack_remaining = attack
        self.release_remaining = None

    def release(self):
        self.release_remaining = release

    def samples(self, linespace):
        global out_keys

        for midi_in in midi.Input.read(self)