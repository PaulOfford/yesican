from settings_code import Settings

settings = Settings()

run_state = 3  # see constants.py for a list of run states

eng_rpm = 0
pre_calc_gear = 0
speed = 0
clutch_depressed = False
brake_pressure = 0


def get_run_state() -> int:
    return run_state


def set_run_state(desired_run_state: int) -> None:
    global run_state
    run_state = desired_run_state
