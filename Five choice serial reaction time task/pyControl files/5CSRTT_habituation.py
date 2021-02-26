"""Task file for 5-CSRTT habituation, task starts with reward and trial starts by presenting all light
of the five-choice light on for undefined time any poke at five_choice give reward

reward ==> five choice all lights on ==> reward

Important readouts:
Responses :- #Correct_response (can also rename as Responses )

"""

from pyControl.utility import *
import hardware_definition as hw

# list of states
states = ['choice',
          'reward']


# list of events
events = ['session_timer',
          'poke_1',             # light 1
          'poke_2',             # light 2
          'poke_3',             # light 3
          'poke_4',             # light 4
          'poke_5',             # light 5
          'poke_6',             # reward receptacle in
          'poke_6_out',         # reward receptacle out
          'port_lights_timer',  # turn off five choice light and advance to limited hold(LH) stage
          'reward_in_timer',    # turn off reward port light to reinforce to leave receptacle
          'penalty_omission']   # timer to wait for response for defined period

# initial state name (required by pyControl)
initial_state = 'reward'

# variables
v.steps_rate = 2000
v.n_steps = 1500
v.session_duration = 30 * minute # Session duration


def run_start():
    # Set session timer and turn on houslight.
    set_timer('session_timer', v.session_duration)
    hw.reward_port.SOL.on() # turn on house light - we use reward port SOL to power house light


def run_end():
    # Turn off all hardware outputs.
    hw.off() # turn off house light - we use reward port SOL to power house light


def reward(event):
    if event == 'entry': 
        hw.syringe_pump.backward(v.steps_rate, v.n_steps)
        hw.reward_port.LED.on()
    elif event == 'exit':
        hw.reward_port.LED.off()
        hw.speaker.off()
    elif event == 'poke_6_out' or event == 'poke_6':
        hw.reward_port.LED.off()
        print('reward_obtained')
        goto_state('choice')

# turn on all 5-choice llight and wait for response 
def choice(event):
    if event == 'entry':          
        hw.five_poke.poke_1.LED.on() # 5-choice hole_1 light on
        hw.five_poke.poke_2.LED.on() # 5-choice hole_2 light on
        hw.five_poke.poke_3.LED.on() # 5-choice hole_3 light on
        hw.five_poke.poke_4.LED.on() # 5-choice hole_4 light on
        hw.five_poke.poke_5.LED.on() # 5-choice hole_5 light on
    elif event == 'exit':
        hw.syringe_pump.backward(v.steps_rate, v.n_steps)
        hw.five_poke.poke_1.LED.off() # 5-choice hole_1 light off
        hw.five_poke.poke_2.LED.off() # 5-choice hole_2 light off
        hw.five_poke.poke_3.LED.off() # 5-choice hole_3 light off
        hw.five_poke.poke_4.LED.off() # 5-choice hole_4 light off
        hw.five_poke.poke_5.LED.off() # 5-choice hole_5 light off
        hw.speaker.off()
    elif event == 'poke_1' or event == 'poke_2' or event == 'poke_3' or event == 'poke_4' or event == 'poke_5':
        hw.five_poke.poke_1.LED.off() # 5-choice hole_1 light off
        hw.five_poke.poke_2.LED.off() # 5-choice hole_2 light off
        hw.five_poke.poke_3.LED.off() # 5-choice hole_3 light off
        hw.five_poke.poke_4.LED.off() # 5-choice hole_4 light off
        hw.five_poke.poke_5.LED.off() # 5-choice hole_5 light off
        print('Correct_response') # count to number of 5-choice poke
        goto_state('reward')



def all_states(event):
    # When 'session_timer' event occurs stop framework to end session.
    if event == 'session_timer':
        stop_framework()

