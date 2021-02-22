from pyControl.utility import *
import hardware_definition as hw
from devices import *

#### States and events.
# --------------------------------------------------------------------------------------

states = [ 'detect_run', 'trial_start', 'motor_forward', 'delay', 'detect_lick_go',
          'give_reward', 'punishment', 'detect_lick_nogo', 'motor_backward', 'ITI', 'stim_interval',
         'fp_timeout', 'ts_timeout', 'TTL_wait', 'rest', 'run_start', 'run_end' , 'linear_fwd', 'linear_back', 'detect_task']
          
          


events = ['sessionTimer',
	      'started_running',
          'stopped_running',
          'run_timer',
          'lick_event',
          'motorAtWhiskers',
          'motorAtStart',
          'lickWindow',
          'solenoidOff',  
          'vel',
		  'TTL_out',
		  'TTL_in',
		  'delay_end']

initial_state = 'TTL_wait'


#### set the parameters of the task here
# --------------------------------------------------------------------------------------
## time between texture switch and moving linear linear_stage
v.timetoforward = 500 #msec

## time for linear stage to move to the desired position
v.stageMoveTime = 600 #msec

# session parameters
v.reward_time = 180 # time that the solenoid is open during rewards (ms)

# trial parameters, to change across mice and training phases
v.lick_window = 2.5 # reward time window during which mouse has to lick (s)
v.delay = 50 #the actual length of this is the number here plus 1/3 of the time the linear stage takes to move back. It is time after stimulation  that the mice must withold licking before the auditory cue (ms)
v.rewardDelay = 100 #time delay between correct go trial and reward
v.fp_timeoutLength = 10 #length of time out after false positive trials
v.ts_timeoutLength = 0.3 #length of timeout in too soon trails. This can be very short.
v.ITI = 5 # the inter-trial interval (Seconds). The actual time between one motor_atwhisk and the following is v.iti+v.lickwindow+(v.stagetomove*2)
v.chanceGo = 0.5 # chance of a go trial
v.num_rewards = 0 # the number of rewards delivered
v.stimLen = 1000 #time that the pole is in the whiskers (ms)


# running parameters
v.run_time = 100       # Time subject must run to start trial. (ms)
v.velocity_threshold = 10 # Set appropriate to setup, units are encoder cm/second.


# stepper motor parameters
##### this is an important variable. See the task 'motor.py'
initialPos = 75
v.goPos = initialPos - 26 #  set to 5 for switch test, to 26 for normal training . #add the number of desired steps 
v.nogoPos = initialPos - 5 #  set to 26 for switch test, to 5 for normal training .#the position of the motor in nogo trial (steps)change between -60 (easier) and -40 (harder)
v.speed = 840 #speed of the motor (steps/second)


# auditory cue parameters make this longer than the reward time
v.cueLen = 1000 #the length of the auditory cue (ms)
v.frequency = 5000 #frequency of the cue (Hz)
v.cueVol = 1 #volume of the cue (db?)
v.punishmentVol = 150 #volume of white noise punishment



##### initialise global task variables
# --------------------------------------------------------------------------------------

v.consecGo = 0 # count the number of consecutive go and nogo trials
v.consecNoGo = 0
v.num_rewards = 0 #the number of rewarded trials


##### imaging variables

# the number of sessions (to later be merged) that have so far occured
v.numSessions = 0

# whether or not the behaviour should be paused due to the imaging
v.pauseBehav = False


v.reverse = False

# count the number of trials
v.trial_counter = 0

###### instantiate rotary encoder
# -----------------------------------------------------------------------------------

running_wheel = Rotary_encoder(name='running_wheel', sampling_rate=30, output='velocity',
                               threshold=v.velocity_threshold, rising_event='started_running',
                               falling_event='stopped_running', reverse=v.reverse)
							   
							   

# Run start and stop behaviour.
def run_start():

	print('session started')
	
	print('duration of lick window is (s)%s' %v.lick_window)
		
	print('withold time is (s) %s' %v.delay)
	
	print('reward before delay is %s' %v.rewardDelay)
		
	print('chance of go trials is %s' %v.chanceGo)
	
	print('nogo position is %s' %v.nogoPos)
	
	print('go position is %s' %v.goPos)

	running_wheel.record()       
	#hw.solenoid.off()
	hw.Lickometer.SOL_2.off()


    
def run_end():
	#hw.ir_led.off()   
	hw.off() # Turn off hardware outputs.

def TTL_wait(event):
	print('waiting for TTL')
	if event == 'TTL_in':
		goto_state('detect_task')
	
	
	
def detect_task(event):
    
	if event == 'entry':     
		if v.pauseBehav == True:
			timed_goto_state('rest',5*ms)
		else:
			timed_goto_state('trial_start', 5*ms)

	
		# if abs(running_wheel.velocity) > v.velocity_threshold: # Subject already running when state entered.
			# set_timer('run_timer', v.run_time)
			# print('mouse already running')
            
	# elif event == 'started_running': # Subject has started running
		# set_timer('run_timer', v.run_time)
	# elif event == 'stopped_running': # Subject has stopped running
		# disarm_timer('run_timer')
	# elif event == 'lick_event':
		# disarm_timer('run_timer')
		# goto_state('time_out')
	# elif event == 'run_timer': # Subject has run long enough to trigger trial start.
		# goto_state('trial_start')
        
        
        
def trial_start(event):
    # randomly choose whether it's a go or nogo trial
	
    if event == 'entry':

		hw.linearStage_trig2.on() #trig2 is backward. this actually means off. One of the two triggers reads high as off and low as on. It's switched.
		hw.linearStage_trig1.off() #trig 1 is forward. this is also off, so here we're turning the motor off
	     
		v.trial_counter = v.trial_counter+1
		print('number of trials presented is %s' %v.trial_counter)
				
	
		v.isGo = withprob(v.chanceGo)

		if v.isGo == True:
			v.isNoGo = False
		else:
			v.isNoGo = True

		# do not have more than 3 consecutive go or nogo trials
		if v.consecNoGo > 2 or v.isGo == True and v.consecGo < 4:
			print('goTrial')
			v.isGo = True
			
			v.consecGo += 1
			v.consecNoGo = 0
			
			# the pyboard needs a few ms to process this function
			timed_goto_state('motor_forward',5*ms)
    	       
		elif v.consecGo > 2 or v.isNoGo == True:
    		
			print('nogo_trial')
			v.isGo = False
			
			v.consecNoGo += 1
			v.consecGo = 0
			
			# the pyboard needs a few ms to process this function
			timed_goto_state('motor_forward', 5*ms)



def motor_forward(event):
    if event == 'entry': 
        if v.isGo == True:
            # the motor should arrive at the whisker coincidently with the 'stim_interval' state
            #timed_goto_state('stim_interval', (v.goPos/v.speed) * 4 * second)
            timed_goto_state('linear_fwd', (v.goPos/v.speed) * 4 * second)

            hw.stepper.forward(v.speed, v.goPos)
        else:
            #timed_goto_state('stim_interval', (v.nogoPos/v.speed) * 4 * second)
            timed_goto_state('linear_fwd', (v.goPos/v.speed) * 4 * second)

            hw.stepper.forward(v.speed, v.nogoPos)


def linear_fwd(event):
    if event == 'entry':
        hw.linearStage_trig1.on() ### calculate how long it takes for it to arrive?
        timed_goto_state('stim_interval', v.stageMoveTime*ms)#it goes into stim interval when linear stage reaches the fwd position

        

def stim_interval(event):
    # the time the motor stays at the whiskers
    if event == 'entry':
    	hw.linearStage_trig1.off()
        print('motor at whiskers')
        timed_goto_state('linear_back', v.stimLen * ms)

def linear_back(event):
    if event=='entry':
        hw.linearStage_trig2.off() #trig2 is backward. this actually means on. One of the two triggers reads high as off and low as on. It's switched.
        timed_goto_state('delay', (v.stageMoveTime/3)*ms)



def delay(event):
    # the delay period in which the mouse must not lick
	if event == 'entry':
		# need to set response cue volume early to fix bug
		print('linear stage at initial position')
		
		set_timer('delay_end', v.delay * ms)
		
	if event == 'delay_end':
		if v.isGo == True:
			goto_state('detect_lick_go')
		else:
			goto_state('detect_lick_nogo')
		
	if event == 'lick_event':
		disarm_timer('delay_end')
		if v.isGo == True:
			print('tooSoon')
			timed_goto_state('ts_timeout', 0) #, 20*ms)
		else:
			timed_goto_state('detect_lick_nogo', 0)#, 20*ms) #this is basically a grace period. If it licks very early in nogo trials, we don't rise the false positive outcome

		#if event == 'lick_event':
		#print('tooSoon')
		#timed_goto_state('time_out', 20*ms)
        
    
def detect_lick_go(event):

    set_timer('lickWindow', v.lick_window * second)
                       
    if event == 'lick_event':
    
               
        disarm_timer('lickWindow')
        #v.trial_counter += 1
        timed_goto_state('give_reward', v.rewardDelay)
               
    elif event == 'lickWindow':
        
        print('missed trial')
        goto_state('motor_backward')
        
        
   
def detect_lick_nogo(event):
    
    set_timer('lickWindow', (v.lick_window * second))
    
    if event == 'lick_event':
        
        print('false positive trial')
        goto_state('fp_timeout')
        
    elif event == 'lickWindow':
        
        print('correct rejection')
        goto_state('motor_backward')   
        
    
    
def give_reward(event):

    if event == 'entry':
        print('correct trial') 
        v.num_rewards += 1
        print('waterON')
        #hw.solenoid.on()
        hw.Lickometer.SOL_2.on()

        set_timer('solenoidOff', v.reward_time*ms)
    
    if event == 'solenoidOff':
        #hw.solenoid.off()
		hw.Lickometer.SOL_2.off()

		goto_state('motor_backward')   
        

def fp_timeout(event):
    if event == 'entry':
		#seems to work setting volume here just before sound, may cause a future bug though
        print('start fp_timeout of %s seconds' %v.fp_timeoutLength)

        timed_goto_state('motor_backward', v.fp_timeoutLength * second)
    if event == 'exit':
        pass

#def punishment(event):
 #  if event == 'entry':
  #      #seems to work setting volume here just before sound, may cause a future bug though
   #    hw.speaker.set_volume(v.punishmentVol)
    #   hw.speaker.noise()
     #  print('start timeout of %s seconds' %v.punishmentLength)
#
 #      timed_goto_state('ITI', v.punishmentLength * second)
  # if event == 'exit':
   #    hw.speaker.off()		
		
		
def ts_timeout(event):
	if event == 'entry':
		print('start ts_timeout of %s seconds' %v.ts_timeoutLength) 
		timed_goto_state('motor_backward', v.ts_timeoutLength*second)
	if event == 'lick_event':
		goto_state('ts_timeout')


def motor_backward(event):    
	if event == 'entry':
		if v.isGo == True:   
			timed_goto_state('ITI', v.goPos/v.speed * second)
			hw.stepper.backward(v.speed, v.goPos)
		else:
			timed_goto_state('ITI', v.nogoPos/v.speed * second)
			hw.stepper.backward(v.speed, v.nogoPos)
        

        
def ITI(event):
    if event == 'entry':
        print('ITI')
        
        timed_goto_state('detect_task', v.ITI*second)
		
def rest(event):
	if event == 'entry':
		print('into rest state')
	if event == 'TTL_in':
		goto_state('detect_task')
		


def all_states(event):

	if event == 'TTL_out':
		print('End of imaging session %s' %v.numSessions)
		v.pauseBehav = True
	if event == 'TTL_in':
		v.pauseBehav = False
		v.numSessions += 1
		print('beginning of imaging session %s' %v.numSessions)


	if event == 'lick_event':
		print('lick')
