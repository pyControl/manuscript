# Device driver file for the PokeA and PokeB devices used in the maze hardare definition.
# These devices are used to allow two IR beams and two LEDs to be connected to a 
# single behaviour port.

import pyControl.hardware as _h

class PokeA():
    # Single IR beam, LED and Solenoid using ports DIO_A and POW_A.
    def __init__(self, port, rising_event = None, falling_event = None, debounce = 5):
        self.input = _h.Digital_input(port.DIO_A, rising_event, falling_event, debounce)
        self.LED = _h.Digital_output(port.POW_A)

    def value(self):
        return self.input.value()

class PokeB():
    # Single IR beam, LED and Solenoid  using ports DIO_B and POW_B.
    def __init__(self, port, rising_event = None, falling_event = None, debounce = 5):
        self.input = _h.Digital_input(port.DIO_B, rising_event, falling_event, debounce)
        self.LED = _h.Digital_output(port.POW_B)
        
    def value(self):
        return self.input.value()