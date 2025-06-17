import time
from settings_code import Settings

settings = Settings()

run_state = 3  # see constants.py for a list of run states

eng_rpm = 0
pre_calc_gear = 0
speed = 0
clutch_depressed = False
brake_pressure = 0
pedal_position = 0

pending_race_start = True

race_start_time = 0

starting_fuel_level = 0
previous_fuel_level = 1000  # we use a high number here to force the initial display of the projected fuel level
current_fuel_level = 0
fuel_burn_rate = 0  # in litres per minute


def get_run_state() -> int:
    return run_state


def set_run_state(desired_run_state: int) -> None:
    global run_state
    run_state = desired_run_state
