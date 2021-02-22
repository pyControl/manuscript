#--------------------------5-CSRTT Variable iti Protocol Task File----------------------

# cue presentation ==> Correct response       ==> reward(@reward port)      ==> iti(long)** ==> cue presentation
# cue presentation ==> Incorrect response     ==> penalty (house light off) ==> iti(long)** ==> cue presentation
# cue presentation ==> omission (no response) ==> penalty (house light off) ==> iti(long)** ==> cue presentation
# **any response at 5-Poke during the iti is considered as premature response and trial starts again after penalty(house light off)

# Important readouts:
# Responses :- number of Corrects, number of Incorrects, number of Omissions, number of Prematures
# Latencies :-Reward lat., Premature lat., Correct lat.,

# iti duration randomnly picked by programme from iti list
# important note:- if reward port SOL not used and intended to use 'house_light = Digital_output(pin=board.port_5.POW_A)'
#  ....then this line of code 'hw.reward_port.SOL.on()'  need to modify as 'hw.house_light.on()' to control HouseLight 

#--------------------------------------------------------------------------


# necessary imports to begin code

from pyControl.utility import *
import hardware_definition as hw
import random


# list of states and events

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
          'penalty_omission']   # timer to wait for response for defined period

# initial state name (required by pyControl)
initial_state = 'start'

# variables
# variables changes according to stages
iti_list    = [7, 9, 11, 13] # iti list values represents in sec, can be changed accornding to experiment
v.state_dur = 20 * second    # cue stimulus duration


#constant variable for all stages

v.session_dur   = 30 * minute  # Session duration
v.LH_dur        = 2 * second   # limited hold duration
v.reward_in_dur = 2 * second   # reward duration this duration
v.penalty_dur   = 5 * second   # penalty duration(All lights off)
v.steps_rate    = 1000         # step rate for stepper motor if you want to use peristaltic pump
v.n_steps       = 1300         # number of steps for stepper motor if you want to use peristaltic pump
v.target        = 0
v.ITI_dur       = 0            # this duration randomly select from the above list


# states defines starts and ending of task file
def run_start():
    set_timer('session_timer', v.session_dur)
    hw.reward_port.SOL.on() # turn on house light - we use reward port SOL to power house light


def run_end():
    hw.off() # Turn off the Hardware
    hw.reward_port.SOL.off() # turn off house light - we use reward port SOL to power house light


# initial state
#5-CSRTT always starts by delivering reward
def start(event):
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


# task phase which present random cue
def choice_task(event):
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


# reward state
def reward(event):
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


# penalty state
def penalty(event):
    if event == 'entry':
        print('penalty')
        hw.reward_port.SOL.off()  # house light off
        hw.reward_port.LED.off()  # reward port light off
        timed_goto_state('iti', v.penalty_dur)
    elif event == 'exit':
        hw.reward_port.SOL.on()
    elif event == 'poke_1' \
            or event == 'poke_2' \
            or event == 'poke_3' \
            or event == 'poke_4' \
            or event == 'poke_5':
        print('attempts_dur_penalty')


# iti state
def iti(event):
    if event == 'entry':
        x = random.choice(iti_list)
        v.ITI_dur = x*second
        print('iti_dur:{}'.format(v.ITI_dur))
        print('iti_start_time')
        timed_goto_state('choice_task', v.ITI_dur)
    elif event == 'poke_1' \
            or event == 'poke_2' \
            or event == 'poke_3' \
            or event == 'poke_4' \
            or event == 'poke_5':
        print('Premature_response')
        goto_state('penalty')


# state indipendent behavior
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

