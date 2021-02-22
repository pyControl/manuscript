# Social-decision making task.
#The focal animal is in Maze 2, and recipient is in Maze 1.
#Prosocial side is A, selfish B. 
#The focal can poke in 2A to go to prosocial side (A), giving reward to both animals
# or poke in 2B to go to selfish side (B), giving reward only to itself.

from pyControl.utility import *
import hardware_definition as hw

#---------------------------------------------------
#  STATES AND EVENTS
#---------------------------------------------------

states = ['wait_focal_decision',
          'open_A_doors_for_reward',
          'close_A_doors_for_reward',
          'wait_focal_enter_reward_A',
          'wait_recipient_enter_reward_A',
          'open_recipient_A_door',
          'open_focal_A_door',
          'open_B_doors_for_reward',
          'close_B_doors_for_reward',
          'wait_focal_enter_reward_B',
          'wait_recipient_enter_reward_B',
          'open_recipient_B_door',
          'open_focal_B_door']

events = ['poke_1A',
          'poke_1B',         
          'poke_2A',
          'poke_2B', 
          'IR_1A',
          'IR_1B',
          'IR_1C',
          'IR_2A',
          'IR_2B',
          'IR_2C',
          'feeder_1A',
          'feeder_1A_out',
          'feeder_1B',
          'feeder_1B_out',
          'feeder_2A',
          'feeder_2A_out',
          'feeder_2B',
          'feeder_2B_out',
          'duration_session']

initial_state = 'wait_focal_decision'

#---------------------------------------------------
# VARIABLES
#---------------------------------------------------

v.duration_session = 30*minute  # Duration of the total session
v.change_state = 0.01*second    # Delay to change state
v.delay_doors = 10*second       # Delay to open doors after reward

v.focal_rewards = 0             # Amount of rewards for the focal subject
v.recipient_rewards = 0         # Amount of rewards for the recipient subject
v.pokes_1A_before_decision = 0  # Amount of prosocial pokes the recipient did before the decision
v.pokes_1B_before_decision = 0  # Amount of selfish pokes the recipient did before the decision
v.selfish_choices = 0           # Number of selfish choices
v.prosocial_choices = 0         # Number of prosocial choices

#---------------------------------------------------
#DEFINE BEHAVIOUR
#---------------------------------------------------

def run_start():   #set the session timer on
    set_timer ('duration_session', v.duration_session)

def run_end():  #turn off all hardware outputs
    hw.off()

#---------------------------------------------------

def wait_focal_decision(event):
    #Wait for focal subject (In Maze 2) to decide which reward side to go. 
    if event == 'entry':
        hw.poke_2A.LED.on()
        hw.poke_2B.LED.on()
        print('Number of Prosocial Choices: {}'.format(v.prosocial_choices))
        print('Number of Selfish Choices: {}'.format(v.selfish_choices))
        print('Number of 1A pokes before choice: {}'.format(v.pokes_1A_before_decision))
        print('Number of 1B pokes before choice: {}'.format(v.pokes_1B_before_decision))

    elif event=='poke_2A':   # Recipient subject is trained to go Maze 1A, so 2A is prosocial
        v.prosocial_choices +=1
        goto_state('open_A_doors_for_reward')
        print('PROSOCIAL CHOICE')
        hw.poke_1A.LED.off()
        hw.poke_1B.LED.off()
        hw.poke_2A.LED.off()
        hw.poke_2B.LED.off()

    elif event =='poke_2B':  # Recipient subject is trained to go Maze 1A, so 2B is selfish
        v.selfish_choices +=1
        goto_state('open_B_doors_for_reward')
        print('SELFISH CHOICE')
        hw.poke_1A.LED.off()
        hw.poke_1B.LED.off()
        hw.poke_2A.LED.off()
        hw.poke_2B.LED.off()

    elif event == 'poke_1A':
        v.pokes_1A_before_decision += 1

    elif event == 'poke_1B':
        v.pokes_1B_before_decision += 1


###---------------------------------------------------------------####
#            IF chooses 2A - PROSOCIAL CHOICE

def open_A_doors_for_reward(event):
    # Open both doors (Maze 1 and 2) to access prosocial side reward area
    # Motor of the focal delivers a pellet already
    if event == 'entry':
        hw.door_1A.on()
        hw.door_2A.on()
        hw.motor_2A.forward(step_rate=200, n_steps=200) 
        hw.feeder_2A.LED.on()           
        v.focal_rewards += 1           
        timed_goto_state('close_A_doors_for_reward', v.change_state)


def close_A_doors_for_reward(event):
    # Detect when subjects enter the reward area.
    # Once it detects the first subject, it will jump to another state to detect the other
    if event == 'entry':
        print('waiting IRs A to detect animals')
    if event == 'IR_1A':  #recipient detected first and change state to detect the focal
        hw.door_1A.off()
        goto_state('wait_focal_enter_reward_A')       
    if event == 'IR_2A': #focal detected first and change state to detect recipient 
        hw.door_2A.off()
        goto_state('wait_recipient_enter_reward_A')       


def wait_focal_enter_reward_A(event):
    # Wait for focal to enter reward area to close its door and deliver pellet to recipient
    # After focal detection, wait 10 secs to open recipient door.
    if event == 'entry':
        print('waiting focal to enter reward A')
    if event == 'IR_2A': 
        hw.door_2A.off()
        hw.motor_1A.forward(step_rate=200, n_steps=200)
        hw.feeder_1A.LED.on()        
        v.recipient_rewards += 1   
        timed_goto_state('open_recipient_A_door', v.delay_doors)       
     if event == 'exit':
        hw.feeder_1A.LED.off()  
        hw.feeder_2A.LED.off()  
   

def wait_recipient_enter_reward_A(event):
    # Wait for recipient to enter reward area to close door and deliver pellet 
    # After recipient detection, wait 10 secs to open its door.
    if event == 'entry':
        print('waiting recipient to enter reward A')
    if event == 'IR_1A':
        hw.door_1A.off()
        hw.motor_1A.forward(step_rate=200, n_steps=200)
        hw.feeder_1A.LED.on()        
        v.recipient_rewards += 1   
        timed_goto_state('open_recipient_A_door', v.delay_doors)       
    if event == 'exit':
        hw.feeder_1A.LED.off()  
        hw.feeder_2A.LED.off()  


def open_recipient_A_door(event):
    # Open the door of the recipient to go back to the choice area
    if event == 'entry':
        hw.door_1A.on()
        timed_goto_state('open_focal_A_door', v.change_state)


def open_focal_A_door(event):
    # Recipient in choice area, wait for focal go to choice area to close its door
    # and start a new trial
    if event == 'entry':
        print('Wait recipient to enter choice area to open focal A door')
    if event == 'IR_1B':  # Recipient in choice area, close its door and open focals
        hw.door_1A.off()
        hw.door_2A.on()
    if event == 'IR_2B':  # Focal in choice area, starting a new trial
        hw.door_2A.off()
        goto_state('wait_focal_decision')



###---------------------------------------------------------------####
#            IF chooses 2B - SELFISH CHOICE


def open_B_doors_for_reward(event):
    # Open both doors (Maze 1 and 2) to access selfish side reward area
    # Motor of the focal delivers a pellet
    if event == 'entry':
        hw.door_1B.on()
        hw.door_2B.on()
        hw.motor_2B.forward(step_rate=200, n_steps=200)
        hw.feeder_2B.LED.on()           
        v.focal_rewards += 1  
        timed_goto_state('close_B_doors_for_reward',v.change_state)


def close_B_doors_for_reward(event):
    # Detect when subjects enter the reward area.
    # Once it detects the first subject, it will jump to another state to detect the other
    if event == 'entry':
        print('waiting IRs C to detect animals')
    if event == 'IR_1C':  # recipient gets detected first
        hw.door_1B.off()
        goto_state('wait_focal_enter_reward_B')            
    if event == 'IR_2C':  # focal gets detected first
        hw.door_2B.off()
        goto_state('wait_recipient_enter_reward_B')             


def wait_focal_enter_reward_B(event):
    # Wait for focal to enter reward area to close its door and wait 10 seconds to open recipient's door
    if event =='IR_2C':
        hw.door_2B.off()
        timed_goto_state('open_recipient_B_door', v.delay_doors)
    if event == 'exit':
        hw.feeder_2B.LED.off()  


def wait_recipient_enter_reward_B(event):
    # Wait for recipient to enter reward area to close its door and wait 10 seconds to open it again
    if event =='IR_1C':
        hw.door_1B.off()
        timed_goto_state('open_recipient_B_door', v.delay_doors)
    if event == 'exit':
        hw.feeder_2B.LED.off()  


def open_recipient_B_door(event):
    # Open the door of the recipient to go back to the choice area
    if event == 'entry':
        hw.door_1B.on()
        timed_goto_state('open_focal_B_door', v.change_state)


def open_focal_B_door(event):
    # Recipient in choice area, wait for focal go to choice area to close its door
    # and start a new trial
    if event == 'entry':
        print('Wait for recipient to enter choice area to open focal B door')
    if event == 'IR_1B':  # Recipient in choice area, close its door and open focals
        hw.door_1B.off()
        hw.door_2B.on()
    if event == 'IR_2B':  # Focal in choice area, starting a new trial
        hw.door_2B.off()
        goto_state('wait_focal_decision')


#STATE INDEPENDENT BEHAVIOUR
def all_states(event):     #when duration of session event occurs, then stop framework to end session
    if event == 'duration_session':
        stop_framework()
