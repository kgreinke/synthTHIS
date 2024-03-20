# Synthesize THIS

## Name
Created by Kathrine Greinke
For questions outside of the grading process, place them in the nearest shredder. 

## Description
This is a simple python synthesizer that can produce sounds in accordance to the oscillator chosen by the user when prompted. I made it for a course project for CS 410P Music Sound and Computers.

## Usage
This was made and tested only in a windows enviroment and had to utilize a virtual port in order to do midi without spending a lot of money on a midi device. It can be altered to work with a midi device by changing the name on line 243 to the name of the midi device of your choosing. I can not say as to how well the functionality be if you do as I could not personally test it.

The use of VMPK (Virtual MIDI Piano Keyboard) is not required, though some of the functionality is built specifically for the MIDI mapping of VMPK and will produce unexpected results upon trying.

    When using loopMIDI on windows for a virtual port:
        Use the default name in and press the '+' in the bottom left
    
    When using VMPK on windows:
        In the "MIDI Connections" option under the "Edit" tab
            Set MIDI IN Driver to Network
            Set MIDI OUT Driver to Windows MM
            Set Output MIDI Connection to either:
                The name of your midi device (I think)
                or
                The name you designate in loopMIDI when making a virtual port

    After all this is set up, then you can launch the program.
        

## Requirements
For windows users:
    (
        loopMIDI                    -          (https://www.tobias-erichsen.de/software/loopmidi.html)
        and
        VMPK                        -          (https://vmpk.sourceforge.io/)
        or
        other VMPK of your choosing
    )
    or
    (
        A midi device compatible with windows OS
        and
        it's respective software
        or
        VMPK                        -          (https://vmpk.sourceforge.io/)
    )

For non windows users:
    Entirely unknown

## Project status
Functional, some elements still under construction.
