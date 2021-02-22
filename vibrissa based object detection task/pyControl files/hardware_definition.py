
from devices import *

board = Breakout_1_2()

running_wheel = Rotary_encoder(name='running_wheel', sampling_rate=30, output='velocity')

Lickometer = Lickometer(port=board.port_2, rising_event_A='lick_event')

stepper = Stepper_motor(port = board.port_3)

linearStage_forwardTrig  = Digital_output(pin=board.BNC_1) 
linearStage_backwardTrig = Digital_output(pin=board.BNC_2)
