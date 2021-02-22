"""This task is for 5-CSRTT, task starts with reward and trial starts by presenting one of the five-choice
light_on for a defined stimulus duration (state_dur)+ extra time (limited hold where cue light turned off but still mouse
still have chance to make choice) correct poke leads to reward then iti or incorrect and omission leads to time out

*** Presents sound for 1sec during iti to distracts the subject
Correct response ==> reward ==> iti ==> cue presentation

Incorrect response ==> penalty (house light off) ==> iti ==> cue presentation

omission (no response) ==> penalty (house light off) ==> iti ==> cue presentation
Important readouts:
Responses :- #Corrects, #Incorrects, #Omissions, #Prematures
Latencies :-Reward lat., Premature lat., Correct lat.,
"""

# necessary imports to begin code
from pyControl.utility import *
import hardware_definition as hw
import random

# list of states
states = ['start',
          'choice_task',
          'reward',
          'penalty',
          'iti']

# list of events
events = ['session_timer',
          'poke_1',  # light 1
          'poke_2',  # light 2
          'poke_3',  # light 3
          'poke_4',  # light 4
          'poke_5',  # light 5
          'poke_6',  # reward receptacle in
          'poke_6_out',  # reward receptacle out
          'kill_port_lights',  # turn off five choice light and advance to limited hold(LH) stage
          'kill_reward',  # turn off reward port light to reinforce to leave receptacle
          'penalty_omission',  # timer to wait for response for defined period
          'distraction_timer_on',  # timer to present distraction sound on
          'distraction_timer_off']  # timer to present distraction sound off

# initial state name (required by pyControl)

initial_state = 'start'

# variables needed

# variables changes according to stages
v.state_dur = 2 * second  # cue stimulus duration
v.ITI_dur = 5 * second  # inter trial interval duration

# constant variable for all stages
v.session_duration = 30 * minute  # Session duration
v.LH_dur = 2 * second  # limited hold duration
v.reward_stim_dur = 2 * second  # reward duration this duration
v.penalty_dur = 5 * second  # penalty duration(All lights off)
v.steps_rate = 1000  # step rate for stepper motor if you want to use peristaltic pump
v.n_steps = 1300  # number of steps for stepper motor if you want to use peristaltic pump
v.dis_dur = 0
v.target = 0


# states defines starts and ending of task file
def run_start():
    set_timer('session_timer', v.session_duration)
    hw.reward_port.SOL.on()


def run_end():
    hw.off()
    hw.reward_port.SOL.off()


# initial state
def start(event):
    if event == 'entry':
        hw.reward_port.LED.on()
        hw.syringe_pump.backward(v.steps_rate, v.n_steps)
    elif event == 'exit':
        hw.reward_port.LED.off()
        disarm_timer('kill_reward')
    elif event == 'poke_6':
        set_timer('kill_reward', v.reward_stim_dur)
    elif event == 'poke_6_out':
        print("ITI_duration:{} \n SD_duration:{}\n LH_duration:{}".format(v.ITI_dur, v.state_dur, v.LH_dur))
        goto_state('choice_task')


# task phase which present random cue
def choice_task(event):
    if event == 'entry':
        print('Sample_state')
        set_timer('kill_port_lights', v.state_dur)
        set_timer('penalty_omission', (v.state_dur + v.LH_dur))
        v.target = random.randint(1, 5)
        print('v.target:{}'.format(v.target))
        if v.target == 1:
            hw.five_poke.poke_1.LED.on()
        elif v.target == 2:
            hw.five_poke.poke_2.LED.on()
        elif v.target == 3:
            hw.five_poke.poke_3.LED.on()
        elif v.target == 4:
            hw.five_poke.poke_4.LED.on()
        elif v.target == 5:
            hw.five_poke.poke_5.LED.on()
    elif event == 'poke_1' and v.target == 1 \
            or event == 'poke_2' and v.target == 2 \
            or event == 'poke_3' and v.target == 3 \
            or event == 'poke_4' and v.target == 4 \
            or event == 'poke_5' and v.target == 5:
        print('Correct_response')
        goto_state('reward')
    elif event == 'poke_1' and v.target != 1 \
            or event == 'poke_2' and v.target != 2 \
            or event == 'poke_3' and v.target != 3 \
            or event == 'poke_4' and v.target != 4 \
            or event == 'poke_5' and v.target != 5:
        print('Incorrect_response')
        goto_state('penalty')
    elif event == 'exit':
        hw.five_poke.poke_1.LED.off()
        hw.five_poke.poke_2.LED.off()
        hw.five_poke.poke_3.LED.off()
        hw.five_poke.poke_4.LED.off()
        hw.five_poke.poke_5.LED.off()
        disarm_timer('kill_port_lights')
        disarm_timer('penalty_omission')


# reward state
def reward(event):
    if event == 'entry':
        hw.reward_port.LED.on()
    elif event == 'exit':
        hw.reward_port.LED.off()
        disarm_timer('kill_reward')
    elif event == 'poke_6':
        hw.syringe_pump.backward(v.steps_rate, v.n_steps)
        print('Reward_taken')
        set_timer('kill_reward', v.reward_stim_dur)
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
	# randomly select time to present sound
        x = random.randint(500, 3500)
        v.dis_dur = x * ms
        print('iti_start_time')
        timed_goto_state('choice_task', v.ITI_dur)
        set_timer('distraction_timer_on', v.dis_dur)
        set_timer('distraction_timer_off', (v.dis_dur + 1000))
    elif event == 'poke_1' \
            or event == 'poke_2' \
            or event == 'poke_3' \
            or event == 'poke_4' \
            or event == 'poke_5':
        print('Premature_response')
        hw.speaker.set_volume(5)
        hw.speaker.off()
        disarm_timer('distraction_timer_on')
        disarm_timer('distraction_timer_off')
        goto_state('penalty')


# catch-all state
def all_states(event):
    # When 'session_timer' event occurs stop framework to end session.
    if event == 'session_timer':
        print("Event Closing")
        stop_framework()
    elif event == 'kill_port_lights':
        hw.five_poke.poke_1.LED.off()
        hw.five_poke.poke_2.LED.off()
        hw.five_poke.poke_3.LED.off()
        hw.five_poke.poke_4.LED.off()
        hw.five_poke.poke_5.LED.off()
    elif event == 'kill_reward':
        hw.reward_port.LED.off()
    elif event == 'penalty_omission':
        print('omission')
        goto_state('penalty')
    elif event == 'poke_1' or event == 'poke_2' or event == 'poke_3' or event == 'poke_4' or event == 'poke_5':
        print('5_poke_entries')
    elif event == 'poke_6_out':
        print('receptacle_entries')
    elif event == 'distraction_timer_on':
        hw.speaker.set_volume(35)
        hw.speaker.noise()
    elif event == 'distraction_timer_off':
        hw.speaker.set_volume(5)
        hw.speaker.off()

