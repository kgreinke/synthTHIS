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
from scipy.io import wavfile
import mido

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
keyboard = mido.open_input()


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


# *********************************************************************************************
# Purpose:      Converts a midi key into a frequency 
# Parameters:   key         -> holds an integer representation of the midi key
# Returns:      {float}     -> float representation of the frequency of the key passed in
# *********************************************************************************************
def key_to_frequency(key):
    return 440 * 2**((key - 69) / 12)


# *********************************************************************************************
# Purpose:      Generates a numpy linespace given a frame count 
# Parameters:   frames          -> hold the number of frames in to generate in a sample
# Returns:      {np.linespace}  -> object holding an array of sample times starting at clock
# *********************************************************************************************
def linespace_generator(frames):
    line = np.linspace(sample_clock / sample_rate,
                       (sample_clock + frames) / sample_rate,
                       frames,
                       dtype=np.float32)
    return line

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

    # ******************************************************************************************
    # Purpose:          Set note's release time remaining
    # Parameters:       self        -> object being queried
    # ******************************************************************************************
    def release(self):
        self.release_remaining = release

    # ******************************************************************************************
    # Purpose:          Sample generator for note object to create and shape a wave
    # Parameters:       self        -> object being played
    #                   linespace   -> object holding the linespace data for the note
    # Return:           samples     -> numpy array with a wave to be played
    # ******************************************************************************************
    def samples(self, linespace):
        if self.playing == False:
            return None
        
        freq = self.frequency
        count = len(linespace)

        #determine oscillator type currently in use
        if osc_type == 'sine':
            samples = sine_wave(freq, linespace)
        elif osc_type == 'square':
            samples = square_wave(freq, linespace)
        else:
            samples = saw_wave(freq, linespace)

        #calculate release 
        if self.release_remaining is not None:
            release_copy = self.release_remaining
            if release_copy <= 0:
                self.playing = False
                return None
            
            start_gain = release_copy / release
            end = count / sample_rate
            release_copy -= end
            end_gain = release_copy / release

            envelope = np.clip(np.linspace(start_gain, end_gain, count), 0.0, 1.0)

            samples *= envelope

            self.release_remaining = max(0, release_copy)

        #calculate attack
        elif self.attack_remaining > 0.0:
            attack_copy = self.attack_remaining
            if attack_copy <= 0:
                self.playing = False
                return None
            
            start_gain = 1.0 - attack_copy / attack
            end = count / sample_rate
            attack_copy -= end
            end_gain = 1.0 - attack_copy / attack

            envelope = np.clip(np.linspace(start_gain, end_gain, count), 0.0, 1.0)

            samples *= envelope

            self.attack_remaining = max(0, attack_copy)

        return samples

#               - - End Of Note Class --                #

# ******************************************************************************************
# Purpose:          Funtion called by sounddevice to get some samples to output.    
# Parameters:       data        -> samples to be made into sound
#                   count       -> integer representation of the frame count
#                   status      -> status of the callback
# ******************************************************************************************
def output_callback(data, count, status):
    global sample_clock

    if status:
        print("output callback:", status)

    samples = np.zeros(count, dtype=np.float32)

    if out_keys:
        line = linespace_generator(count)

        on = list(out_keys.keys())
        off = set()

        for key in on:
            note = out_keys[key]
            note_samples = note.samples(line)
            if note_samples is None:
                off.add(key)
                continue
            samples += note_samples

        for key in off:
            del out_keys[key]

    keys = len(out_keys)
    if keys <= 8:
        samples *= 1.0 / 8.0
    else:
        samples *= 1.0 / len(out_keys)

    #reshape samples
    data[:] = np.reshape(samples, (count, 1))

    sample_clock += count


# ******************************************************************************************
# Purpose:          Process MIDI events accordingly    
# Parameters:       data        -> samples to be made into sound
#                   count       -> integer representation of the frame count
#                   status      -> status of the callback
# ******************************************************************************************
def process_midi_event():
    global out_keys, osc_type

    message = keyboard.recieve()