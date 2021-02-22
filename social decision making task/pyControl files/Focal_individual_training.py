# Two choice task for individual training of the decision-maker during the social-decision task.
# The subject has to poke once in any of the 2 poke-choices to access the food pellet, delivered by a stepper motor in the reward areas. 
# After 10 seconds in the reward area, the door will open to allow the animal go back to the choice area and start a new trial.

from pyControl.utility import *
import hardware_definition as hw

#---------------------------------------------------
#  STATES AND EVENTS
#---------------------------------------------------

states = ['pokes_active',
          'door_A_open1',
          'door_A_close1',
          'reward_A',
          'door_A_open2',
          'door_A_close2',
          'door_B_open1',
          'door_B_close1',
          'reward_B',
          'door_B_open2',
          'door_B_close2']

events = ['poke_1A',
          'poke_1B',         
          'IR_1A',
          'IR_1B',
          'IR_1C',
          'feeder_1A',
          'feeder_1A_out',
          'feeder_1B',
          'feeder_1B_out',
          'duration_session']

initial_state = 'pokes_active' 

#---------------------------------------------------
# VARIABLES
#---------------------------------------------------
v.duration_session = 30*minute  #duration of the total session
v.motor = 1*second #duration of motor rotation for pellet delivery
v.change = 0.01*second #time to change the states
v.change10 = 10*second #time to open door in reward area
v.rewards_A = 0 # number of rewards in 1A side
v.rewards_B = 0 # number of rewards in 1B side
v.block_door = 2 #Variable to block a specific reward area - check line 95 and 100

#-------------------------------------------------------------------------
# Arrays
#-------------------------------------------------------------------------
from array import array
array_size = 0
v.time_to_eat = 0
v.reward_time = 0
v.eating_time = 0

time_to_eat_A = array('f', 0 for i in range(array_size)) # Array to store the time to eat each trial in reward area A.
time_to_eat_B = array('f', 0 for i in range(array_size)) # Array to store the time to eat each trial in reward area B.
time_to_choose = array('f', 0 for i in range(array_size)) # Array to store the time to choose since the trials start.

#---------------------------------------------------
#DEFINE BEHAVIOUR
#---------------------------------------------------
def run_start():   #set the session timer on
    set_timer ('duration_session', v.duration_session)

def run_end():  #turn off all hardware outputs
    hw.off()

#---------------------------------------------------
# Start of a new trial
#---------------------------------------------------

def pokes_active(event):                                
    if event == 'entry':
        v.block_door = 2 #reset variable to block the doors at start of each trial
        v.start_trial = get_current_time()
        hw.poke_1A.LED.on()
        hw.poke_1B.LED.on()
        print('Time to eat per trial in A: {}'.format(time_to_eat_A)) 
        print('Time to eat per trial in B: {}'.format(time_to_eat_B))
        print('Time to choose per trial: {}'.format(time_to_choice))  
        print('Rewards in A: {}'.format(v.rewards_A))
        print('Rewards in B: {}'.format(v.rewards_B))

    if event == 'exit':
        hw.poke_1A.LED.off()
        hw.poke_1B.LED.off()
        v.choice = get_current_time()
        time_to_choose.append((v.choice-v.start_trial)/1000)

    if v.block_door == 0:  # block poke A
        if event == 'poke_1B':                            
            print('Subject chose side B, A side blocked')
            timed_goto_state('door_B_open1', v.change)

    if v.block_door == 1: # block poke B
        if event == 'poke_1A':                            
            print('Subject chose side A, B side blocked')
            timed_goto_state('door_A_open1', v.change)

    elif event == 'poke_1A':                            
        print('Subject chose side A')
        timed_goto_state('door_A_open1', v.change)

    elif event == 'poke_1B':
        print('Subject chose side B')
        timed_goto_state ('door_B_open1', v.change)

#----------------------------------------------------------------
# If subject chooses side A
#----------------------------------------------------------------

def door_A_open1(event):
    # Door for accesing reward area 1A opens and the motor rotates to deliver a pellet into the feeder
    if event == 'entry':
        hw.door_1A.on()
        hw.motor_1A.forward(step_rate=200) 
        timed_goto_state('door_A_close1', v.motor)
    elif event == 'exit':
        hw.motor_1A.off()
        hw.feeder_1A.LED.on()

def door_A_close1(event):
    # Wait for animal to be detected by IR in reward area 1A to close the door
    if event == 'entry':
        print('waiting IR 1A to detect subject')
    elif event == 'IR_1A':
        hw.door_1A.off()
        timed_goto_state ('reward_A', v.change)
        v.reward_time = get_current_time()


def reward_A(event):
    # 10 seconds state for the animal to retrieve the food pellet
    if event == 'entry':
        v.rewards_A += 1
        timed_goto_state('door_A_open2', v.change10)
    if event == 'exit':
        hw.feeder_1A.LED.off()
    elif event == 'feeder_1A_out':  #animal retrieved the food pellet
        v.eating_time = get_current_time()
        v.time_to_eat = ((v.eating_time-v.reward_time)/1000) # Append into the array the time the subject took to eat the reward since entered in the reward area
        time_to_eat_A.append(v.time_to_eat)

def door_A_open2(event):
    # Open reward 1A door after 10 seconds
    if event == 'entry':
        hw.door_1A.on()
        print('door_A is open')
        timed_goto_state ('door_A_close2', v.change)

def door_A_close2(event):
    # Wait for the animal to be detected by IR in choice area to close the door
    if event == 'entry':
        print('waiting IR B to detect subject')
    elif event == 'IR_1B':
        hw.door_1A.off()       
        timed_goto_state ('pokes_active', v.change)

#----------------------------------------------------------------
# If subject chooses side B
#----------------------------------------------------------------

def door_B_open1(event):
    # Door for accesing reward area 1B opens and the motor rotates to deliver a pellet into the feeder
    if event == 'entry':
        hw.door_1B.on()
        hw.motor_1B.forward(step_rate=200) 
        timed_goto_state('door_B_close1',v.motor)
    elif event == 'exit':
        hw.motor_1B.off()
        hw.feeder_1B.LED.on()

def door_B_close1(event):
    # Wait for animal to be detected by IR in reward area 1B to close the door
    if event == 'entry':
        print('waiting IR 1C to detect subject')
    elif event == 'IR_1C':
        hw.door_1B.off()
        timed_goto_state ('reward_B', v.change)
        v.reward_time = get_current_time()

def reward_B(event):
    # 10 seconds state for the animal to retrieve the food pellet
    if event == 'entry':
        v.rewards_B += 1
        timed_goto_state('door_B_open2', v.change10)
    if event == 'exit':
        hw.feeder_1B.LED.off()
    elif event == 'feeder_1B_out':  #animal retrieved the food pellet
        v.eating_time = get_current_time()
        v.time_to_eat = ((v.eating_time-v.reward_time)/1000) # Append into the array the time(s) the subject took to eat the reward 
        time_to_eat_B.append(v.time_to_eat)

def door_B_open2(event):
    # Open reward 1A door after 10 seconds
    if event == 'entry':
        hw.door_1B.on()
        timed_goto_state ('door_B_close2', v.change)

def door_B_close2(event):
    # Wait for the animal to be detected by IR in choice area to close the door
    if event == 'entry':
        print('waiting IR B to detect subject')
    elif event == 'IR_1B':
        hw.door_1B.off()   
        timed_goto_state ('pokes_active', v.change)

#STATE INDEPENDENT BEHAVIOUR

def all_states(event):     #when duration of session event occurs, then stop framework to end session and print variables
    if event == 'duration_session':
        print('Total rewards in A: {}'.format(v.rewards_A))
        print('Total rewards in B: {}'.format(v.rewards_B))     
        print('Time to eat per trial in A: {}'.format(time_to_eat_A)) 
        print('Time to eat per trial in B: {}'.format(time_to_eat_B))
        print('Time to choose per trial: {}'.format(time_to_choice))       
        stop_framework()
