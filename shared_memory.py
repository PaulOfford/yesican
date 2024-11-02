from settings import *

settings = Settings()

eng_rpm = 0
pre_calc_gear = 3
speed = 0

pit_speed_limit = 50  # kph - this is a default setting

root = None

no_of_modes = 2  # this is a default value that gets modified as soon as the code runs
current_mode = 0  # 0 - Gear Shift, 1 - Pit Speed, 2 - Config
desired_mode = 0

flash_window = False
