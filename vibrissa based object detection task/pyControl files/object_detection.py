from pyControl.utility import *
import hardware_definition as hw
from devices import *

# States and events. -------------------------------------------------

states = ['trial_start', 
          'linear_forward',
          'stim_interval',                 
          'delay', 
          'response_window_go',
          'response_window_nogo',
          'give_reward', 
          'ITI', 
          'fp_timeout', 
          'ts_timeout']

events = ['lick_event',
          'window_timer',
          'stim_timer',
          'delay_timer']

initial_state = 'trial_start'

# Task Parameters ---------------------------------------------------

v.stageMoveTime = 600*ms         # time for linear stage to move to position

# session parameters
v.rewardTime = 180*ms          # Reward solenoid open duration.

# trial parameters
v.lick_window = 2.5*second      # Time window after simulus presentation for mouse to lick/withold.
v.delayDur = 50*ms                 # Time after stimulation that the mice must withold licking.
v.rewardDelay = 100*ms          # time delay between correct go trial and reward
v.fp_timeoutLength = 10*second  # length of time out after false positive trials
v.ts_timeoutLength = 0.3*second # length of timeout in too soon trails. This can be very short.
v.ITI = 5*second                # ITI duration.
v.GoProb = 0.5                  # Probability of a go trial
v.stimLen = 1000*ms             # time that the pole is in the whiskers.

# stepper motor parameters

v.goPos = 49   # Number of steps to move stepper motor for Go position.
v.nogoPos = 70 # Number of steps to move stepper motor for NoGo position.
v.speed = 840  # Speed to run the motor (steps/second).

# Task Variables ----------------------------------------------------

v.trial_counter = 0 # Number of trials
v.num_rewards = 0   # Number of rewarded trials
v.consecGo   = 0    # Number of consecutive go trials
v.consecNoGo = 0    # Number of consecutive nogo trials
                          
# Run start and stop behaviour. -------------------------------------

def run_start():
    hw.running_wheel.record()       

def run_end():
    hw.off() # Turn off hardware outputs.

# State behaviour functions  ---------------------------------------- 
        
def trial_start(event):
    # Chose whether trial is go or nogo, tigger stepper motor to
    # set AP position of pole.
    
    if event == 'entry':

        hw.linearStage_backwardTrig.off()
        hw.linearStage_forwardTrig.off()
         
        v.trial_counter += 1
        print('Trial number: %s' %v.trial_counter)
                
        # Determine whether current trial is go or nogo.
        if v.consecNoGo > 2: # Do not allow 3 consecutive nogo trials.
            v.GoTrial = True 
        elif v.consecGo > 2: # Do not allow 3 consecutive go trials.
            v.GoTrial = False
        else:
            v.GoTrial = withprob(v.GoProb) 

        if v.GoTrial:
            print('goTrial')
            v.consecGo += 1
            v.consecNoGo = 0
            hw.stepper.forward(step_rate=v.speed, n_steps=v.goPos)
            timed_goto_state('linear_forward', (v.goPos/v.speed)*second)
        else:
            print('NogoTrial')
            v.consecNoGo += 1
            v.consecGo = 0
            hw.stepper.forward(step_rate=v.speed, n_steps=v.nogoPos)
            timed_goto_state('linear_forward', (v.goPos/v.speed)*second)

def linear_forward(event):
    # Move pole into wiskers using linear stage.
    if event == 'entry':
        hw.linearStage_forwardTrig.on()
        timed_goto_state('stim_interval', v.stageMoveTime)
    elif event == 'exit':
        hw.linearStage_forwardTrig.off()

def stim_interval(event):
    # Hold pole in whiskers for stimLen duration. Subject must withhold licking.
    if event == 'entry':
        timed_goto_state('delay', v.stimLen)
    elif event == 'lick_event':
            print('Premature response')
            goto_state('ts_timeout')
    elif event == 'exit':
        hw.linearStage_backwardTrig.on() # Move pole out of whisker field, stage stops automatically when it reaches home position.

def delay(event):
    # Delay before response window. Subject must withhold licking.
    if event == 'entry':
        if v.GoTrial:
            timed_goto_state('response_window_go', v.delayDur)
        else:
            timed_goto_state('response_window_nogo', v.delayDur)
    elif event == 'lick_event':
            print('Premature response')
            goto_state('ts_timeout')


def response_window_go(event):
    # Response window on go trials, lick triggers reward.
    if event == 'entry':
        set_timer('window_timer', v.lick_window)                 
    elif event == 'lick_event':  
        disarm_timer('window_timer')
        print('correct trial') 
        timed_goto_state('give_reward', v.rewardDelay)   
    elif event == 'window_timer':
        print('missed trial')
        goto_state('ITI')
        
def response_window_nogo(event):
     # Response window on nogo trials, lick triggers timeout.
    if event == 'entry':
        set_timer('window_timer', v.lick_window)        
    elif event == 'lick_event':
        print('false positive trial')
        goto_state('fp_timeout')
    elif event == 'window_timer':
        print('correct rejection')
        goto_state('ITI')   
        
def give_reward(event):
    # Deliver reward.
    if event == 'entry':
        v.num_rewards += 1
        hw.Lickometer.SOL_1.on()
        timed_goto_state('ITI', v.rewardTime)
    elif event == 'exit':
        hw.Lickometer.SOL_1.off() 
        
def fp_timeout(event):
    # Timout following a false positive trial.
    if event == 'entry':
        print('start fp_timeout of %s seconds' %v.fp_timeoutLength/second)
        timed_goto_state('ITI', v.fp_timeoutLength)

def ts_timeout(event):
    # Timeout following a response that is too early.
    if event == 'entry':
        print('start ts_timeout of %s seconds' %v.ts_timeoutLength/second) 
        timed_goto_state('ITI', v.ts_timeoutLength)

def ITI(event):
    # Inter trial interval, move stepper motor back to initial posisition.
    if event == 'entry':
        timed_goto_state('trial_start', v.ITI)
        if v.GoTrial:
            hw.stepper.backward(step_rate=v.speed, n_steps=v.goPos)
        else:
            hw.stepper.backward(step_rate=v.speed, n_steps=v.nogoPos)