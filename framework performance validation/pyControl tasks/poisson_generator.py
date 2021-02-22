# Generates rising/falling edges on the two poisson_output_pins  at the rate
# specified by poisson_rate.

from pyControl.utility import *
from devices import *

# Define hardware.

poisson_output_pin_1 = Digital_output('X3')
poisson_output_pin_2 = Digital_output('X4')

# States and events.
  
states= ['state_1']

events = ['poisson_toggle_1',
          'poisson_toggle_2']

initial_state = 'state_1'

# Variables

v.poisson_rate = 200 # Hz

# Define behaviour.

def run_start():
    v.poisson_int = 1000//v.poisson_rate
    poisson_output_pin_1.toggle()
    set_timer('poisson_toggle_1', exp_rand(v.poisson_int))
    poisson_output_pin_2.toggle()
    set_timer('poisson_toggle_2', exp_rand(v.poisson_int))

def state_1(event):
    if event == 'poisson_toggle_1':
        poisson_output_pin_1.toggle()
        set_timer('poisson_toggle_1', exp_rand(v.poisson_int))
    elif event == 'poisson_toggle_2':
        poisson_output_pin_2.toggle()
        set_timer('poisson_toggle_2', exp_rand(v.poisson_int))