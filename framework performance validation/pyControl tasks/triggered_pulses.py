# Generates a fixed duration pulse each time an external input triggers.

from pyControl.utility import *
from devices import *
import gc

high_load  = True  # Determines whether additional inputs are recorded.
control_GC = True   # Determines whether the time of garbage collection is controlled.

# Define hardware.

output_pin = Digital_output('Y12')
input_pin = Digital_input('Y11', rising_event='trigger', debounce=False)

if high_load:
    poisson_input_pin_1 = Digital_input('X3', rising_event='poisson_rising_1', falling_event='poisson_falling_1', debounce=False)
    poisson_input_pin_2 = Digital_input('X4', rising_event='poisson_rising_2', falling_event='poisson_falling_2', debounce=False)
    analog_input_1 = Analog_input('X5', 'Analog1', 1000)
    analog_input_2 = Analog_input('X6', 'Analog2', 1000)

# States and events.
  
states= ['output_on',
         'output_off']

events = ['trigger']

if high_load:
    events += ['poisson_rising_1',
               'poisson_falling_1',
               'poisson_rising_2',
               'poisson_falling_2']

initial_state = 'output_off'

# Variables

v.pulse_dur = 10     # ms

# Define behaviour.

def run_start():
    if high_load:
        analog_input_1.record()
        analog_input_2.record()

def output_off(event):
    if event == 'entry':
        if control_GC:
            gc.collect()
    elif event == 'trigger':
        goto_state('output_on')


def output_on(event):
    if event == 'entry':
        output_pin.on()
        timed_goto_state('output_off', v.pulse_dur)
    elif event == 'exit':
        output_pin.off()
