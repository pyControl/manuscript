# Task used to test the maximum rate at which the framework can respond
# to digital inputs.  An external squarewave input in connected to pins
# Y2 and Y3 triggering state transitions on each edge.  The frequency
# of the input is then increased until the framework crashes.

from pyControl.utility import *
from devices import *

# Define hardware.

digital_input_1 = Digital_input('Y2', rising_event='rising_evt', falling_event=None, debounce=False)
digital_input_2 = Digital_input('Y3', rising_event=None, falling_event='falling_evt', debounce=False)

# States and events.
  
states= ['state_1',
         'state_2']

events = ['rising_evt',
          'falling_evt']

initial_state = 'state_1'

# Define behaviour.

def state_1(event):
    if event == 'rising_evt':
        goto_state('state_2')

def state_2(event):
    if event == 'falling_evt':
        goto_state('state_1')
