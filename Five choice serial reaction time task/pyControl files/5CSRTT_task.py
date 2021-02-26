#--------------------------5-CSRTT Protocol----------------------

# Task file for 5-CSRTT task which can be used for training stages 1-5, and all challanges, by adjusting task variables as described below. 

# One of the five_poke LEDs turns on randomly (cue presentation) and subject has to make response within the specified period of time(SD+LH)
# cue presentation ==> Correct poke (illuminated hole)                  ==> reward(@reward port)      ==> iti** ==> cue presentation
# cue presentation ==> Incorrect response (other than illuminated hole) ==> penalty (house light off) ==> iti** ==> cue presentation
# cue presentation ==> omission (no response)                           ==> penalty (house light off) ==> iti** ==> cue presentation
 
# Important readouts:
# Responses :- number of Corrects, number of Incorrects, number of Omissions, number of Prematures
# Latencies :-Reward lat., Premature lat., Correct lat.,

# If Subject made criteria for two consecutive days, then task can be advanced to stage-1 to satge-2 and so on upto stage-5.
# Detailed description and criteria list is provided in the manuscript 

# VARIABLES CHANGED ACROSS TRAINING STAGES AND CHALLANGES

# Stage 1: v.state_dur = 20 *second , v.ITI_dur = 2 *second
# Stage 2: v.state_dur = 8 *second  , v.ITI_dur = 2 *second
# Stage 3: v.state_dur = 8 *second  , v.ITI_dur = 5 *second
# Stage 4  v.state_dur = 4 *second  , v.ITI_dur = 5 *second
# Stage 5: v.state_dur = 2 *second  , v.ITI_dur = 5 *second

# Attention Challenge 1000ms : v.state_dur = 1 *second    , v.ITI_dur = 5 *second
# Attention Challenge 800ms  : v.state_dur = 0.8 *second  , v.ITI_dur = 5 *second
# FixedITI Challenge         : v.state_dur = 2 *second    , v.ITI_dur = 9 *second
# VariableITI challange      : v.variable_ITI = True
# Sound distraction challange: v.sound_distraction = True

#--------------------------------------------------------------------------

# Imports

from pyControl.utility import *
import hardware_definition as hw
import random

# States and events

states = ['start',
          'choice_task', #Cue Light presentation
          'reward',      #Reward Statefor correct response
          'penalty',     #time out HouseLight off
          'iti']         #inter-trial interval

events = ['session_timer',      # timer to terminate session after defined time (30min usually)
          'poke_1',             # light 1
          'poke_2',             # light 2
          'poke_3',             # light 3
          'poke_4',             # light 4
          'poke_5',             # light 5
          'poke_6',             # reward receptacle in
          'poke_6_out',         # reward receptacle out
          'port_lights_timer',  # turn off five choice light and advance to limited hold(LH) stage
          'reward_in_timer',    # turn off reward port light to reinforce to leave receptacle
          'penalty_omission',   # timer to wait for response for defined period
          'distraction_on_timer',  # timer to turn distractor sound on
          'distraction_off_timer'] # timer to turn distractorsound off

initial_state = 'start'

# Variables

# Paramters adjusted for different training stages and challanges.

v.state_dur = 20 * second      # cue stimulus duration
v.ITI_dur   = 2 * second       # inter trial interval duration
v.variable_ITI = False         # whether to use variable ITI.
v.sound_distraction = False    # whether to use sound distraction.

# Other parameters.

v.session_dur   = 30 * minute  # Session duration
v.LH_dur        = 2 * second   # limited hold duration
v.reward_in_dur = 2 * second   # reward duration this duration
v.penalty_dur   = 5 * second   # penalty duration(All lights off)
v.steps_rate    = 1000         # step rate for stepper motor if you want to use peristaltic pump
v.n_steps       = 1300         # number of steps for stepper motor if you want to use peristaltic pump
v.target        = 0

# Run start and end behaviour.

def run_start():
    set_timer('session_timer', v.session_dur)
    hw.house_light.on() # turn on house light - we use reward port SOL to power house light


def run_end():
    hw.off() # Turn off the Hardware
    hw.house_light.off() # turn off house light - we use reward port SOL to power house light

# State behaviour functions.

def start(event):
	# 5-CSRTT always starts by delivering reward
    if event == 'entry':
        hw.reward_port.LED.on()                           # turn on reward port LED on
        hw.syringe_pump.backward(v.steps_rate, v.n_steps) # beginning reward
    elif event == 'exit':
        hw.reward_port.LED.off()
        disarm_timer('reward_in_timer')
    elif event == 'poke_6':
        set_timer('reward_in_timer', v.reward_in_dur) # timer to turn off rewrard stim after speified time(2sec usually) 
    elif event == 'poke_6_out':
        print("ITI_duration:{} \n SD_duration:{}\n LH_duration:{}".format(v.ITI_dur, v.state_dur, v.LH_dur))
        goto_state('choice_task')


def choice_task(event):
	# task phase which present random cue
    if event == 'entry':
        print('Sample_state')
        set_timer('port_lights_timer', v.state_dur)
        set_timer('penalty_omission', (v.state_dur + v.LH_dur))
        v.target = random.randint(1, 5) # randomly select int between 1-5 and variable as v.target 
        print('v.target:{}'.format(v.target))        
        #present cue light according to v.target
        if v.target == 1:
            hw.five_poke.poke_1.LED.on() # 5-choice hole_1 light on
        elif v.target == 2:
            hw.five_poke.poke_2.LED.on() # 5-choice hole_2 light on
        elif v.target == 3:
            hw.five_poke.poke_3.LED.on() # 5-choice hole_3 light on
        elif v.target == 4:
            hw.five_poke.poke_4.LED.on() # 5-choice hole_4 light on
        elif v.target == 5:
            hw.five_poke.poke_5.LED.on() # 5-choice hole_5 light on
    # if event (poke) is same as target , considered as correct response and go to reward state
    elif event == 'poke_1' and v.target == 1 \
            or event == 'poke_2' and v.target == 2 \
            or event == 'poke_3' and v.target == 3 \
            or event == 'poke_4' and v.target == 4 \
            or event == 'poke_5' and v.target == 5:
        print('Correct_response') # the latency between cue presentation and correct response is correct lat.
        goto_state('reward')
    # if event (poke) is other than target, considered as incorrect response and go to penalty state
    elif event == 'poke_1' and v.target != 1 \
            or event == 'poke_2' and v.target != 2 \
            or event == 'poke_3' and v.target != 3 \
            or event == 'poke_4' and v.target != 4 \
            or event == 'poke_5' and v.target != 5:
        print('Incorrect_response') # the latency between cue presentation and incorrect response is incorrect lat
        goto_state('penalty')
    # if event ( no respose) is same as target , considered as omission and go to penalty state
    elif event == 'exit':
        hw.five_poke.poke_1.LED.off()     # 5-choice hole_1 light off
        hw.five_poke.poke_2.LED.off()     # 5-choice hole_2 light off
        hw.five_poke.poke_3.LED.off()     # 5-choice hole_3 light off
        hw.five_poke.poke_4.LED.off()     # 5-choice hole_4 light off
        hw.five_poke.poke_5.LED.off()     # 5-choice hole_5 light off
        disarm_timer('port_lights_timer') # clear timer for 5-Choice port lights
        disarm_timer('penalty_omission')  # clear timer for omission


def reward(event):
	# reward state
    if event == 'entry':
        hw.reward_port.LED.on()
    elif event == 'exit':
        hw.reward_port.LED.off()
        disarm_timer('reward_in_timer')
    elif event == 'poke_6':
        hw.syringe_pump.backward(v.steps_rate, v.n_steps) # Reward after correct resonse and poke into reward receptacle
        print('Reward_taken')                             # the latency between correct and Reward_taken is Reward lat.
        set_timer('reward_in_timer', v.reward_in_dur)
    elif event == 'poke_6_out':
        goto_state('iti')
    elif event == 'poke_1' and v.target == 1 \
            or event == 'poke_2' and v.target == 2 \
            or event == 'poke_3' and v.target == 3 \
            or event == 'poke_4' and v.target == 4 \
            or event == 'poke_5' and v.target == 5:
        print('perseverate')

def penalty(event):
	# penalty state
    if event == 'entry':
        print('penalty')
        hw.house_light.off()  # house light off
        hw.reward_port.LED.off()  # reward port light off
        timed_goto_state('iti', v.penalty_dur)
    elif event == 'exit':
        hw.house_light.on()
    elif event == 'poke_1' \
            or event == 'poke_2' \
            or event == 'poke_3' \
            or event == 'poke_4' \
            or event == 'poke_5':
        print('attempts_dur_penalty')

def iti(event):
	# iti state
    if event == 'entry':
        print('iti_start_time')
        if v.variable_ITI: # Use variable ITI
            rand_ITI_dur = random.choice([7, 9, 11, 13])*second
            print('iti_dur:{}'.format(rand_ITI_dur))
            timed_goto_state('choice_task', rand_ITI_dur)
        else: # Use fixed ITI.
            timed_goto_state('choice_task', v.ITI_dur)
        if v.sound_distraction: # Set timer to trigger distracting stimuli.
            sound_start_delay = random.randint(500, 3500)*ms
            set_timer('distraction_on_timer',  sound_start_delay)        # when to start the sound 
            set_timer('distraction_off_timer', sound_start_delay + 1000) # when to stop the sound 

    elif event == 'poke_1' \
            or event == 'poke_2' \
            or event == 'poke_3' \
            or event == 'poke_4' \
            or event == 'poke_5':
        print('Premature_response') # the latency between iti_start_time and Premature_response is premature lat.
        goto_state('penalty')


# State indipendent behavior

def all_states(event):
    # When 'session_timer' event occurs stop framework to end session.
    if event == 'session_timer':
        print("Event Closing")
        stop_framework()
    elif event == 'port_lights_timer':
        hw.five_poke.poke_1.LED.off()
        hw.five_poke.poke_2.LED.off()
        hw.five_poke.poke_3.LED.off()
        hw.five_poke.poke_4.LED.off()
        hw.five_poke.poke_5.LED.off()
    elif event == 'reward_in_timer':
        hw.reward_port.LED.off()
    elif event == 'penalty_omission':
        print('omission')
        goto_state('penalty')
    # all poke events at 5-choice - for counting 5_poke_entries
    elif event == 'poke_1' or event == 'poke_2' or event == 'poke_3' or event == 'poke_4' or event == 'poke_5':
        print('5_poke_entries')
    elif event == 'poke_6_out':
        print('receptacle_entries')
    elif event == 'distraction_on_timer':
        hw.speaker.set_volume(35)
        hw.speaker.noise()
    elif event == 'distraction_off_timer':
        hw.speaker.set_volume(5)
        hw.speaker.off()