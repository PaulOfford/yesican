from settings import *

settings = Settings()
backend_thread = None

is_linux_os = False

# run_state is used to control the execution and shutdown of yesican
RUN_STATE_RUNNING = 3
RUN_STATE_PENDING_SHUTDOWN = 2
RUN_STATE_AWAITING_BACKEND = 1
RUN_STATE_EXITING = 0

run_state = 3  # 3 - running, 2 - pending shutdown, 1 - waiting for backend to stop, 0 - exiting

eng_rpm = 0
pre_calc_gear = 3
speed = 0

pit_speed_switch = False  # True - closed, False - open

root = None

no_of_modes = 2  # this is a default value that gets modified as soon as the code runs
current_mode = 0  # 0 - Gear Shift, 1 - Pit Speed, 2 - Config
desired_mode = 0

flash_window = False
