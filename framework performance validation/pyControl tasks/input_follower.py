# Toggles the state of output_pin to match the state of input_pin.
# Used to assess response latency and maximum event rates.
# If high_load is True, in addition to monitoring the input pin the 
# task also monitors two additional digial inputs and two analog inputs.

from pyControl.utility import *
from devices import *
import gc

high_load  = False  # Determines whether additional inputs are recorded.
control_GC = True   # Determines whether the time of garbage collection is controlled.

# Define hardware.
input_pin = Digital_input('Y11', rising_event='rising_edge', falling_event='falling_edge', debounce=False)
output_pin = Digital_output('Y12')

if high_load:
    poisson_input_pin_1 = Digital_input('X3', rising_event='poisson_rising_1', falling_event='poisson_falling_1', debounce=False)
    poisson_input_pin_2 = Digital_input('X4', rising_event='poisson_rising_2', falling_event='poisson_falling_2', debounce=False)
    analog_input_1 = Analog_input('X5', 'Analog1', 1000)
    analog_input_2 = Analog_input('X6', 'Analog2', 1000)

# States and events.
  
states= ['output_on',
         'output_off']

events = ['rising_edge',
          'falling_edge']

if high_load:
    events += ['poisson_rising_1',
               'poisson_falling_1',
               'poisson_rising_2',
               'poisson_falling_2']

initial_state = 'output_off'

# Define behaviour.

def run_start():
    if high_load:
        analog_input_1.record()
        analog_input_2.record()

def output_off(event):
    if event == 'entry':
        output_pin.off()
    elif event == 'rising_edge':
        goto_state('output_on')

def output_on(event):
    if event == 'entry':
        output_pin.on()
        if control_GC:
            gc.collect()
    elif event == 'falling_edge':
        goto_state('output_off')