import mido, sounddevice
import numpy as np
import scipy.io.wavfile as wav


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

# soft_toggle               -> holds a boolean of whether the 'soft' button is on for VMPK
#                           -> default: False
soft_toggle = False         

# sustain_toggle            -> holds a boolean of whether the 'sustain' button is on for VMPK
#                           -> default: False
sustain_toggle = False

# -- END - "globals" --


# -- midi startup --
keyboard = mido.open_input('loopMIDI Port 0')


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


def output_callback(data, frames, time_info, status):

    global sample_clock

    if status:
        print("output callback:", status)


    samples = np.zeros(frames, dtype=np.float32)

    if out_keys:
        line = linespace_generator(frames)

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

    nkeys = len(out_keys)
    if nkeys <= 8:
        samples *= 1.0 / 8.0
    else:
        samples *= 1.0 / len(out_keys)

    data[:] = np.reshape(samples, (frames, 1))

    sample_clock += frames


def process_midi_event():
    global out_keys, out_osc

    # wait and grab any message that comes in
    mesg = keyboard.receive()

    mesg_type = mesg.type

    # when a note is being pressed
    #   add a note to the dictionary
    if mesg_type == 'note_on':
        key = mesg.note
        velocity = mesg.velocity / 127
        print('note on', key, mesg.velocity, round(velocity, 2))
        out_keys[key] = Note(key, osc_type)

    # when a note is no longer being pressed
    #   call its release method to end it
    elif mesg_type == 'note_off':
        key = mesg.note
        velocity = round(mesg.velocity / 127, 2)
        print('note off', key, mesg.velocity, velocity)
        if key in out_keys:
            out_keys[key].release()
    
    # for Virtual MIDI Piano Keyboard:
    #   this is called 'bender' but it acts as a pitchwheel
    elif mesg.type == 'pitchwheel':
        pitch = round(mesg.pitch / 127, 2)
        print('bender', mesg.pitch, pitch)
    
    elif mesg.type == 'control_change':
        # for Virtual MIDI Piano Keyboard:
        #   this is the 'Value' knob for the 'Control' dropdown
        #   specifically when '7-Volume' is selected
        if mesg.control == 7:
            control = round(mesg.value / 127, 2)
            print('control', mesg.value, control)
        
        # for Virtual MIDI Piano Keyboard:
        #   this is the 'soft' toggle button
        elif mesg.control == 64:
            if sustain_toggle == True:
                print("sustain_toggle off")
                sustain_toggle = False
            else:
                print("sustain_toggle on")
                sustain_toggle = True

        # for Virtual MIDI Piano Keyboard:
        #   this is the 'soft' toggle button
        elif mesg.control == 67:
            if soft_toggle == True:
                print("soft_toggle off")
                soft_toggle = False
            else:
                print("soft_toggle on")
                soft_toggle = True

        # for Virtual MIDI Piano Keyboard: 
        #   this is the stop button (aka 'panic' button)
        elif mesg.control == 123:
            print("Panic No Longer!")
            return False

    else:
        print('unknown MIDI message', mesg)
    return True

output_stream = sounddevice.OutputStream(
    samplerate=sample_rate,
    channels=1,
    blocksize=block_size,
    callback=output_callback,
)
output_stream.start()

while process_midi_event():
    pass