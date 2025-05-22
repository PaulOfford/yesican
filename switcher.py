import platform
import shared_memory

if platform.system() == 'Linux':
    import RPi.GPIO as GPIO  # import RPi.GPIO module

from my_logger import microsec_message


class Switcher:
    number_of_displays = 0
    target_display_mode = 0
    saved_display_mode = 0  # we use this to jump back to the correct display after switching off the PSI
    in_pit_speed_mode = False

    def __init__(self, frame_list_length):
        self.number_of_displays = frame_list_length

        if platform.system() == 'Linux':
            # choose BOARD or BCM
            GPIO.setmode(GPIO.BCM)  # BCM for GPIO numbering
            GPIO.setup(
                shared_memory.settings.get_pit_switch_gpio_pin(), GPIO.IN, pull_up_down=GPIO.PUD_UP
            )  # pit speed switch input with pull-up
            GPIO.setup(
                shared_memory.settings.get_display_step_gpio_pin(), GPIO.IN, pull_up_down=GPIO.PUD_UP
            )  # display step input with pull-up

            # pit speed switch handlers
            GPIO.add_event_detect(
                shared_memory.settings.get_pit_switch_gpio_pin(),
                GPIO.BOTH,
                callback=self.pit_switch_handler,
                bouncetime=50
            )

            # display step switch handler
            GPIO.add_event_detect(
                shared_memory.settings.get_display_step_gpio_pin(),
                GPIO.FALLING,
                callback=self.display_step_handler(),
                bouncetime=50
            )

    def get_target_display_mode(self) -> int:
        return self.target_display_mode

    def set_target_display_mode(self, target: int):
        self.target_display_mode = target

    def step_display_mode(self) -> None:
        self.target_display_mode = (self.target_display_mode + 1) % self.number_of_displays
        microsec_message(2, "Next button to mode " + str(self.target_display_mode))

    def pit_switch_handler(self):
        # check the physical pit speed limiter switch
        if not GPIO.input(shared_memory.settings.get_pit_switch_gpio_pin()):
            if not self.in_pit_speed_mode:
                # the pit speed switch state has changed
                microsec_message(1, "Switch to Pit Speed display")
                self.saved_display_mode = self.target_display_mode
                self.target_display_mode = 1
                self.in_pit_speed_mode = True
        else:
            if self.in_pit_speed_mode:
                # the pit speed switch state has changed
                microsec_message(1, "Switch to previous display")
                self.target_display_mode = self.saved_display_mode
                self.in_pit_speed_mode = False

    def display_step_handler(self) -> None:
        self.step_display_mode()

    @staticmethod
    def end_gpio():
        # Clean up on exit
        # not used at the moment due to concerns that this may clobber the GPIO-attached display
        GPIO.cleanup()
