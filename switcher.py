import platform

if platform.system() == 'Linux':

    import RPi.GPIO as GPIO  # import RPi.GPIO module

    # choose BOARD or BCM
    GPIO.setmode(GPIO.BCM)  # BCM for GPIO numbering
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # input with pull-up

def is_switch_on() -> bool:
    if platform.system() == 'Linux':
        # as the state is down when the switch is on, we need to invert the return value
        return not GPIO.input(16)
    else:
        return False

def end_gpio():
    # Clean up on exit
    # not used at the moment due to concerns that this may clobber the GPIO-attached display
    GPIO.cleanup()

