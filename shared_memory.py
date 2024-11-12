from settings_code import Settings

settings = Settings()
backend_thread = None
bus_vector = None

is_linux_os = False

run_state = 3  # see constants.py for a list of run states

eng_rpm = 0
pre_calc_gear = 0
speed = 0

pit_speed_switch = False  # True - closed, False - open

root = None

no_of_modes = 2  # this is a default value that gets modified as soon as the code runs
current_mode = 0  # 0 - Gear Shift, 1 - Pit Speed, 2 - Config
desired_mode = 0

flash_window = False


def get_run_state() -> int:
    return run_state


def set_run_state(desired_run_state: int) -> None:
    global run_state
    run_state = desired_run_state
