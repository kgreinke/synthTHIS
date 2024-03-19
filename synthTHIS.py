import mido, sounddevice
import numpy as np
import scipy.io.wavfile as wav
import os

# **********************************************************************************************
#   * Class:            synthTHIS
#   * Purpose:          Simple class to hold and adjust information about VMPK synth setup
#   * Data Members:     osc_type            -> string holding which oscillator type is currently
#                                              being used by the synthesizer
#                                           ->  default - sine
#                                           ->  options: sine, saw, square                      
#
#                       log                 -> represents if verbose mode is activated
#                                           ->  default - False
#                                           ->  options: True, False 
#
#                       sample_rate         -> integer holding the sample rate in sps for
#                                              audio output
#                                           ->  default - 48000
#                                           ->  options - 44100, 48000 
#
#                       block_size          -> samples to process, higher values help with
#                                              slower computers
#                                           ->  default - 16  
#
# {under construction}  soft_toggle         -> holds a boolean of whether the 'soft' button
#                                              is on for VMPK
#                                           ->  default: False
#
# {under construction}  sustain_toggle      -> holds a boolean of whether the 'sustain'
#                                              button is on for VMPK
#                                           ->  default: False 
#
#                       volume              -> holds an integer representation of the volume
#                                              knob for VMPK 
#                                           -> default: 66
# **********************************************************************************************
class synthTHIS:
    # ******************************************************************************************
    # Purpose:          Default constructor
    # ******************************************************************************************
    def __init__(self):
        self.osc_type = 'sine'
        self.log = False  
        self.sample_rate = 48000   
        self.block_size = 16      
        self.out_keys = dict()      
        self.soft_toggle = False       
        self.sustain_toggle = False
        self.volume = 66

    # ******************************************************************************************
    # Purpose:          Print a cool ascii art method with the synth's name
    # ****************************************************************************************** 
    def startup_display(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        art = """
                                     __   .__         ___________ ___ ___  .___   _________._.._.._. 
              ______ ___.__.  ____ _/  |_ |  |__      \__    ___//   |   \ |   | /   _____/| || || | 
             /  ___/<   |  | /    \\   __\|  |  \       |    |  /    ~    \|   | \_____  \ | || || | 
             \___ \  \___  ||   |  \|  |  |   Y  \      |    |  \    Y    /|   | /        \ \| \| \| 
            /____  > / ____||___|  /|__|  |___|  /      |____|   \___|_  / |___|/_______  / __ __ __ 
                \/  \/          \/            \/                      \/               \/  \/ \/ \/ 
                                                                                                 
        """
        print(art)

    # ******************************************************************************************
    # Purpose:          Display current specifications of the synth
    # ******************************************************************************************  
    def current_setup(self):
        print("\n*******************************************************************************\n")
        print(" Here is the current specifications of synthTHIS:")
        print(f"\t1 -- Oscillator Type:     {self.osc_type}")
        print(f"\t2 -- Log Toggle:          {self.log}")
        print(f"\t3 -- Sample Rate:         {self.sample_rate}")
        print(f"\t4 -- Block Size:          {self.block_size}")
        print(f"\t5 -- Soft Toggle:         {self.soft_toggle}")
        print(f"\t6 -- Sustain Toggle:      {self.sustain_toggle}")
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to change configuration of the synth
    # ******************************************************************************************      
    def configuration_tree(self):
        self.current_setup()
        option = int(input("Enter the number from above of the attribute you wish to change: "))
        if option == 1:
            self.change_osc()
        elif option == 2:
            self.change_log()
        elif option == 3:
            self.change_sample_rate()
        elif option == 4:
            self.change_block_size()
        elif option == 5:
            self.change_soft_toggle()
        elif option == 6:
            self.change_sustain_toggle()
        else:
            print("Invalid input, please try again..")
            self.configuration_tree()
        print("\n*******************************************************************************\n")


    # ******************************************************************************************
    # Purpose:          Allow user to change the oscillator
    # ******************************************************************************************    
    def change_osc(self):
        print("\n*******************************************************************************\n")
        print(f"Current oscillator type: {self.osc_type}")
        print("Options: sine, square, and saw")
        print("For example, to change to saw: type saw and hit enter")
        osc = input("Put your choice here: ")
        if osc == 'sine':
            print("Oscillator changed to sine!")
            self.osc_type = 'sine'
        elif osc == 'square':
            print("Oscillator changed to square!")
            self.osc_type = 'square'
        elif osc == 'saw':
            print("Oscillator changed to saw!")
            self.osc_type = 'saw'
        else:
            print("Input was invalid, assigning default.")
            self.osc_type = 'sine'
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to change the log toggle
    # ****************************************************************************************** 
    def change_log(self):
        print("\n*******************************************************************************\n")
        print(f"Changing verbose mode toggle, currently set to {self.log}")
        print("Options: True or False")
        print("For example, to change to True: type T and hit enter")
        TorF = input("Enter your choice here: ")
        if TorF == 'T':
            print("Log turned on!")
            self.log = True
        elif TorF == 'F':
            print("Log turned off!")
            self.log = False
        else:
            print("Input was invalid, assigning default.")
            self.log = False
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to change the sample rate
    # ******************************************************************************************
    def change_sample_rate(self):
        print("\n*******************************************************************************\n")
        print(f"Current sample rate: {self.sample_rate}")
        print("Options: 44100, 48000")
        rate = int(input("Enter the sample rate (44100 or 48000): "))
        if rate == 44100 or rate == 48000:
            print("Sample rate updated successfully!")
            self.sample_rate = rate
        else:
            print("Invalid sample rate, keeping the current value.")
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to change the block size
    # ******************************************************************************************
    def change_block_size(self):
        print("\n*******************************************************************************\n")
        print(f"Current block size: {self.block_size}")
        print("Options: any integer between 1 and 30")
        print("Hint: Changing to a higher value can help with slower computers")
        block = int(input("Enter the desired block size: "))
        if block > 0 and block <= 30:
            print("Block size updated successfully!")
            self.block_size = block
        else:
            print("Invalid block size, keeping the current value.")
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to MANUALLY change the soft_toggle toggle
    # ****************************************************************************************** 
    def change_soft_toggle(self):
        print("\n*******************************************************************************\n")
        print(f"VMPK soft toggle currently set to {self.soft_toggle}")
        print("Options: True or False")
        print("For example, to change to True: type T and hit enter")
        TorF = input("Enter your choice here: ")
        if TorF == 'T':
            print("soft toggle turned on!")
            self.soft_toggle = True
        elif TorF == 'F':
            print("soft toggle turned off!")
            self.soft_toggle = False
        else:
            print("Input was invalid, assigning default.")
            self.soft_toggle = False
        print("\n*******************************************************************************\n")

    # ******************************************************************************************
    # Purpose:          Allow user to MANUALLY change the sustain_toggle toggle
    # ****************************************************************************************** 
    def change_sustain_toggle(self):
        print("\n*******************************************************************************\n")
        print(f"VMPK sustain toggle currently set to {self.sustain_toggle}")
        print("Options: True or False")
        print("For example, to change to True: type T and hit enter")
        TorF = input("Enter your choice here: ")
        if TorF == 'T':
            print("sustain toggle turned on!")
            self.sustain_toggle = True
        elif TorF == 'F':
            print("sustain toggle turned off!")
            self.sustain_toggle = False
        else:
            print("Input was invalid, assigning default.")
            self.sustain_toggle = False
        print("\n*******************************************************************************\n")

#               - - End Of synthTHIS Class --                #


# -- START - "globals" -- #

# attack                    -> float holding the attack time for note synthesis
#                           -> default - 0.020
attack = 0.020

# release                   -> float holding the release time for note synthesis
#                           -> default - 0.10
release = 0.10

# sample_clock              -> tracker of samples output to ensure correctly phased waveforms
#                           -> default - none
sample_clock = 0

# out_keys                  -> dynamic dictionary of currently playing keys 
#                           -> index by MIDI key number 
out_keys = dict()

# --   midi startup  -- #
keyboard = mido.open_input('loopMIDI Port 0')

# --  create global synth  -- #
synth = synthTHIS()

# -- END - "globals" -- #


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
    # Parameters:       key         -> object
    #                   osc         -> oscillator type for note
    # ******************************************************************************************
    def __init__(self, key, osc):
        self.frequency = key_to_frequency(key)
        self.osc_type = osc
        self.playing = True
        self.attack_remaining = attack
        self.release_remaining = None

    # ******************************************************************************************
    # Purpose:          Set note's release time remaining
    # ******************************************************************************************
    def release(self):
        self.release_remaining = release

    # ******************************************************************************************
    # Purpose:          Sample generator for note object to create and shape a wave
    # Parameters:       linespace   -> object holding the linespace data for the note
    # Return:           samples     -> numpy array with a wave to be played
    # ******************************************************************************************
    def samples(self, linespace):
        if self.playing == False:
            return None
        
        freq = self.frequency
        count = len(linespace)

        #determine oscillator type currently in use
        if synth.osc_type == 'sine':
            samples = sine_wave(freq, linespace)
        elif synth.osc_type == 'square':
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
            end = count / synth.sample_rate
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
            end = count / synth.sample_rate
            attack_copy -= end
            end_gain = 1.0 - attack_copy / attack

            envelope = np.clip(np.linspace(start_gain, end_gain, count), 0.0, 1.0)

            samples *= envelope

            self.attack_remaining = max(0, attack_copy)

        return samples

#               - - End Of Note Class --                #


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
    line = np.linspace(sample_clock / synth.sample_rate,
                       (sample_clock + frames) / synth.sample_rate,
                       frames,
                       dtype=np.float32)
    return line

# *********************************************************************************************
# Purpose:      Callback for the purpose of playing audio through sounddevice 
# Parameters:   data            -> data to output
#               frames          -> frame count 
#               time_info       -> info about sample clock
#               status          -> status of callback
# *********************************************************************************************
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


# *********************************************************************************************
# Purpose:      Process midi events as they are happening
# *********************************************************************************************
def process_midi_event():
    global out_keys, out_osc, synth

    # wait and grab any message that comes in
    mesg = keyboard.receive()

    mesg_type = mesg.type

    # when a note is being pressed
    #   add a note to the dictionary
    if mesg_type == 'note_on':
        key = mesg.note
        velocity = mesg.velocity / 127
        if synth.log is True: print('note on', key, mesg.velocity, round(velocity, 2))
        out_keys[key] = Note(key, synth.osc_type)

    # when a note is no longer being pressed
    #   call its release method to end it
    elif mesg_type == 'note_off':
        key = mesg.note
        velocity = round(mesg.velocity / 127, 2)
        if synth.log is True: print('note off', key, mesg.velocity, velocity)
        if key in out_keys:
            out_keys[key].release()
    
    # for Virtual MIDI Piano Keyboard:
    #   this is called 'bender' but it acts as a pitchwheel
    elif mesg.type == 'pitchwheel':
        pitch = round(mesg.pitch / 127, 2)
        if synth.log is True: print('bender', mesg.pitch, pitch)
    
    elif mesg.type == 'control_change':
        # for Virtual MIDI Piano Keyboard:
        #   this is the 'Value' knob for the 'Control' dropdown
        #   specifically when '7-Volume' is selected
        if mesg.control == 7:
            synth.volume = round(mesg.value / 127, 2)
            if synth.log is True: print('volume', mesg.value, synth.volume)
        
        # for Virtual MIDI Piano Keyboard:
        #   this is the 'soft' toggle button
        elif mesg.control == 64:
            if synth.sustain_toggle == True:
                if synth.log is True: print("sustain_toggle off")
                synth.sustain_toggle = False
            else:
                if synth.log is True: print("sustain_toggle on")
                synth.sustain_toggle = True

        # for Virtual MIDI Piano Keyboard:
        #   this is the 'soft' toggle button
        elif mesg.control == 67:
            if synth.soft_toggle == True:
                if synth.log is True: print("soft_toggle off")
                synth.soft_toggle = False
            else:
                if synth.log is True: print("soft_toggle on")
                synth.soft_toggle = True

        # for Virtual MIDI Piano Keyboard: 
        #   this is the stop button (aka 'panic' button)
        elif mesg.control == 123:
            print("Panic No Longer!")
            return False

    else:
        print('unknown MIDI message', mesg)
    return True


# ***************************************************************************
#   Main function for calling methods and printing results
# ***************************************************************************
synth.startup_display()
synth.current_setup()

# output stream setup
output_stream = sounddevice.OutputStream(
    samplerate=synth.sample_rate,
    channels=1,
    blocksize=synth.block_size,
    callback=output_callback,
)
output_stream.start()

run = True
while run is True:
    print("Would you like to:")
    print("\t1 - start synth")
    print("\t2 - check synth configuration")
    print("\t3 - change synth configuration")
    print("\t4 - exit program")
    option = int(input("Enter the number of the desired option: "))

    if option == 1:
        while process_midi_event():
            pass
    elif option == 2: synth.current_setup()
    elif option == 3: synth.configuration_tree()
    elif option == 4: quit()
    else:
        print("Invalid option, try again...")
        break
    