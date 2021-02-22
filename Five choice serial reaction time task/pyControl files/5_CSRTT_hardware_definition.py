# This hardware definition is to implement 5-CSRTT with specified hardare/circuit boards below:- 
# 1)Five poke(five_poke)
# 2)Single Nose poke(reward_port) 
# 3)House Light(house_light)
# 4)Speaker
# 5)Stepper Motor based Peristaltic pump/Syringe pump(syringe_pump)

from devices import *

board = Breakout_1_2() # Instantiate breakout board.

# Instantiate Five Poke
# Port 1 on the Five poke board is connected to port 1 on the breakout board.
# Port 2 on the Five poke board is connected to port 3 on the breakout board.
five_poke = Five_poke(ports=[board.port_1, board.port_3])

# Intantiate reward port poke plugged into port 2 on breakout board.
reward_port = Poke(port=board.port_2, rising_event='poke_6', falling_event='poke_6_out')

# Instantiate audio board plugged into port 4 on breakout board.
speaker = Audio_board(port=board.port_4)

# Instantiate syringe pump stepper motor plugged into port 5 on breakout board.
syringe_pump = Stepper_motor(port=board.port_5)

#-----------------------------------------------
# House light is connected to reward port’s solenoid output. 
house_light = reward_port.SOL