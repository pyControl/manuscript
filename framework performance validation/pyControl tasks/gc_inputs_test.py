# Task used to test the effect of garbage collection on digital inputs. 
# An input signal comprising 1ms pulses every 10 ms was connected to 
# pins Y1, Y2 and Y3.  A timer is used to trigger garbage collection 1ms
# before one out of every 10 input pulses, allowing the effect of 
# garbage collection on input processing to be assessed by analysing
# the resulting data file.

from pyControl.utility import *
from devices import *
import gc

# Define hardware.

digital_input_1 = Digital_input('Y1', rising_event='rising_1', falling_event='falling_1', debounce=False)
digital_input_2 = Digital_input('Y2', rising_event='rising_2', falling_event=None, debounce=False)
digital_input_3 = Digital_input('Y3', rising_event=None, falling_event='falling_3', debounce=False)

# States and events.
  
states= ['state_1',
         'state_2']

events = ['rising_1',
          'rising_2',

          'falling_1',
          'falling_3',
          'trigger_gc']


initial_state = 'state_1'

# Define behaviour.

def state_1(event):
    if event == 'rising_2':
        set_timer('trigger_gc', 9*ms, output_event=True)
    elif event == 'trigger_gc':
        gc.collect()
        goto_state('state_2')

def state_2(event):
    if event == 'entry':
        timed_goto_state('state_1', 100*ms)
