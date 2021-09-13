# Toggles the state of output_pin 

from pyControl.utility import *
from devices import *

# Define hardware.
output_pin = Digital_output('Y1')

input_pin_1 = Digital_input('Y2', rising_event='rising_1', falling_event='falling_1', debounce=False, pull='down')
input_pin_2 = Digital_input('Y3', rising_event='rising_2', falling_event='falling_2', debounce=False, pull='down')
input_pin_3 = Digital_input('Y4', rising_event='rising_3', falling_event='falling_3', debounce=False, pull='down')
input_pin_4 = Digital_input('Y5', rising_event='rising_4', falling_event='falling_4', debounce=False, pull='down')
input_pin_5 = Digital_input('Y6', rising_event='rising_5', falling_event='falling_5', debounce=False, pull='down')

# States and events.
  
states= ['output_on',
         'output_off']

events = ['rising_1',
          'rising_2',
          'rising_3',
          'rising_4',
          'rising_5',
          'falling_1',
          'falling_2',
          'falling_3',
          'falling_4',
          'falling_5']

initial_state = 'output_off'

# Define behaviour.

def output_off(event):
    if event == 'entry':
        timed_goto_state('output_on', 100)
        output_pin.off()


def output_on(event):
    if event == 'entry':
        timed_goto_state('output_off',100)
        output_pin.on()
        