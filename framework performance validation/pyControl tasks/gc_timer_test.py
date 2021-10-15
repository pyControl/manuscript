# Task to test the effect of garbage collection on pyControl timers.
# Timers are used to toggle one output on and off every 1ms and annother
# every 5ms.  Garbage collection occurs intermittantly and the effect
# on the timers can be assessed by analysing recordings of the output
# signals.

from pyControl.utility import *
from devices import *

# Define hardware.
output_1 = Digital_output('Y11')
output_2 = Digital_output('Y12')

# States and events.
  
states= ['state_1']

events = ['timer_1',
          'timer_2']

initial_state = 'state_1'

# Variable.

v.delay_1=1
v.delay_2=5

# Define behaviour.

def run_start():
    output_1.on()
    output_2.on()
    set_timer('timer_1', v.delay_1)
    set_timer('timer_2', v.delay_2)

def state_1(event):
    if event == 'timer_1':
        output_1.toggle()
        set_timer('timer_1', v.delay_1)
    elif event == 'timer_2':
        output_2.toggle()
        set_timer('timer_2', v.delay_2)
