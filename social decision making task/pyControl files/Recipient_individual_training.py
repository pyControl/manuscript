# One-forced choice task for individual training of the recipient subject during the social-decision task (Maze 1A)
# The subject has to poke an increasing number of times given by the block number (pokes_for_reward). The number
# of successful trials per block can be changed according to the needs (trials_per_block).
# The experimenter can set the starting nose-poke ratio at the beginning of the session by changing the block_number.

from pyControl.utility import *
import hardware_definition as hw

#---------------------------------------------------
#  STATES AND EVENTS
#---------------------------------------------------

states = ['poke_active',
          'door_A_open1',
          'door_A_close1',
          'reward_A',
          'reward_consumed_A',
          'door_A_open2',
          'door_A_close2']

events = ['duration_session',
          'poke_1A',
          'poke_1B',
          'IR_1A',
          'IR_1B',
          'IR_1C',
          'feeder_1A',
          'feeder_1A_out']

initial_state = 'poke_active'

#---------------------------------------------------
# VARIABLES
#---------------------------------------------------
v.duration_session = 30*minute  # Duration of the total session
v.motor = 1*second              # Duration of motor rotation for pellet delivery
v.change = 0.01*second          # Time to change state
v.change10 = 10*second          # Time to open door after reward
v.time_since_last_poke = 0      # Time between pokes if happen.
v.rewards_A = 0                 # Number of rewards in 1A side
v.poke_time = 0
v.previous_poke_time = 0
v.block_number = 0              # Block number the subject is currently on.
v.pokes_for_reward = [2,3,4,5,6,7,8,9,10] # Number of pokes needed for reward in each block of trials.
v.trials_per_block = 5          # Number of successful trials needed to move to next block.
v.previous_trials_ok = True
v.succ_trials_this_block =0     # Number of sucessful trials
v.number_trials = 0             # Total amount of trials per block
v.pokes_this_trial = 0          # Number of pokes on the current trial
v.unsuccessful_trial = 0        # Number of non-sucessful trials

from array import array
array_size = 0
v.time_to_eat = 0
v.reward_time = 0
v.eating_time = 0

time_to_eat_A = array('f', 0 for i in range(array_size)) # Create an array of floats of size array_size, initialising each value to 0.
                                                         # This array saves the time from pellet delivery until the subject takes it for each trial

#---------------------------------------------------
#DEFINE BEHAVIOUR
#---------------------------------------------------

def run_start():   #set the session timer on
    set_timer ('duration_session', v.duration_session)

def run_end():  #turn off all hardware outputs
    hw.off()


#---------------------------------------------------
#INCREASING POKE-RATIO PROTOCOL
#---------------------------------------------------

def poke_active(event):
    # Wait for the recipient to nose-poke the specific number of times determined by the block number the subject is in.
    # If the time between pokes is less than 2 secs it counts as a succesfull trial to move over the blokcs. 
    if event == 'entry':
        hw.poke_1A.LED.on()
        v.pokes_this_trial = 0 #Setting number of pokes made by the subject to 0 at start of new trial
        v.previous_trials_ok = True
        print('Pokes this trial: {}'.format(v.pokes_this_trial))  # This variables are helpful to see in which poke-ratio the subject is
        print('Block number: {}'.format(v.block_number))        
        print('Nº of successful trials this block: {}'.format(v.succ_trials_this_block)) 
        print('Nº of unsuccesstul trials this block: {}'.format(v.unsuccessful_trial))

    elif event == 'poke_1A':
        v.poke_time = get_current_time()
        if v.pokes_this_trial == 0:
          v.time_since_last_poke = 0
        else:
          v.time_since_last_poke = v.poke_time - v.previous_poke_time
        v.previous_poke_time = v.poke_time
        if (v.time_since_last_poke < 2000 and v.previous_trials_ok==True): # This pokke was between 1 and 2000 ms after last poke.
            v.pokes_this_trial += 1
            if v.pokes_this_trial == v.pokes_for_reward[v.block_number]: # Subject has done enough pokes to meet the criterion for this block.
                v.succ_trials_this_block += 1
                v.number_trials += 1
                if v.succ_trials_this_block == v.trials_per_block: # Subject has done enough trials to move to next block.
                    v.block_number += 1
                    v.unsuccessful_trial=0
                    v.number_trials = 0
                    v.succ_trials_this_block=0
                timed_goto_state('door_A_open1', v.change)
        else:   #Time between pokes more than 2 secs, so the trial counts as unsuccessfu.
            v.previous_trials_ok = False
            v.pokes_this_trial += 1
            if v.pokes_this_trial == v.pokes_for_reward[v.block_number]:
                v.number_trials += 1
                v.unsuccessful_trial += 1
                v.block_number += 0
                timed_goto_state('door_A_open1',v.change)
    if event == 'exit':
        hw.poke_1A.LED.off()


#---------------------------------------------------
# REWARD PROTOL
#---------------------------------------------------

def door_A_open1(event):
    # Door to access the reward area opens and motor rotates to deliver a reward pellet into the feeder
    if event == 'entry':
        hw.door_1A.on()
        hw.motor_1A.forward(step_rate=200) 
        timed_goto_state('door_A_close1',v.motor)
    if event == 'exit':
        hw.motor_1A.off()
        hw.feeder_1A.LED.on()

def door_A_close1(event):
    # Wait for IR to detect subject in reward area to close the door.
    if event == 'entry':
        print('waiting IR A to detect subject')
    elif event == 'IR_1A':
        hw.door_1A.off()
        timed_goto_state ('reward_A', v.change)
        v.reward_time = get_current_time()

def reward_A(event):
    # 10 seconds state for the subject to retrieve the pellet 
    if event == 'entry':
        v.rewards_A += 1
        timed_goto_state('door_A_open2', v.change10)
    if event == 'exit':
        hw.feeder_1A.LED.off()
    elif event == 'feeder_1A_out': #subject retrieved the food pellet
        v.eating_time = get_current_time()
        v.time_to_eat = ((v.eating_time-v.reward_time)/1000) # Append into the array the time (s) the subject took to eat the reward 
        time_to_eat_A.append(v.time_to_eat)

def door_A_open2(event):
    #Open A door to go back to choice area
    if event == 'entry':
        hw.door_1A.on()
        timed_goto_state ('door_A_close2', v.change)

def door_A_close2(event):
    # Wait for the subject to be detected by IR in choice area to close the door
    if event == 'entry':
        print('waiting IR B to detect subject')
    elif event == 'IR_1B':
        hw.door_1A.off()
        timed_goto_state ('poke_active', v.change)

#---------------------------------------------------
#STATE INDEPENDENT BEHAVIOUR
#---------------------------------------------------

def all_states(event):     #when session finishes, then stop framework to end session and print saved variables
    if event == 'duration_session':
        print('Rewards obtained: {}'.format(v.rewards_A))
        print('Final block number: {}'.format(v.block_number))
        print('Number of trials this block: {}'.format(v.number_trials))
        print('Number of  successful trials this block: {}'.format(v.succ_trials_this_block))
        print('Time to eat per trial in A: {}'.format(time_to_eat_A)) 
        stop_framework()
