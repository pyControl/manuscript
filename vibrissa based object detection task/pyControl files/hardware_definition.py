
from devices import * 
  
board = Breakout_1_2() # Instantiate breakout board.
  
# Instantiate Rotary encoder (currently only supported on port 1). 
running_wheel = Rotary_encoder(name='running_wheel', sampling_rate=30,
                               output='velocity') 
  
# Instantiate lickometer connected to breakout board port 2. 
Lickometer = Lickometer(port=board.port_2, rising_event_A='lick_event') 
  
# Instantiate stepper motor controller connected to breakout board port 3.
stepper = Stepper_motor(port=board.port_3) 
  
# Instantiate digital outputs used to control linear stage on BNC connectors.
linearStage_forwardTrig  = Digital_output(pin=board.BNC_1) 
linearStage_backwardTrig = Digital_output(pin=board.BNC_2)