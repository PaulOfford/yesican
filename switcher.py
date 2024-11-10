import platform

if platform.system() == 'Linux':

    import RPi.GPIO as GPIO  # import RPi.GPIO module

    # choose BOARD or BCM
    GPIO.setmode(GPIO.BCM)  # BCM for GPIO numbering
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # input with pull-up

def is_switch_on() -> bool:
    if platform.system() == 'Linux':
        return GPIO.input(16)
    else:
        return False

def end_gpio():
    # Clean up on exit
    GPIO.cleanup()

