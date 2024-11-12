# You can edit this file to customise your display.
# Be careful not to change the structure of the variables
# as this will cause program exceptions and the yesican won't run.
# Make a backup copy of this file before modifying it.
import configparser

class Settings:
    config = configparser.ConfigParser()

    led_off_color = 'white'
    default_gear_color = 'white'
    default_speed_color = 'white'
    default_blk_color = 'gray20'

    led_radius = 16
    led_good = "lawn green"
    led_warning = "yellow"
    led_alert = "red"

    no_of_leds = 11

    shift_triggers = None
    pit_triggers = None

    def __init__(self):
        self.config.read('config.ini')

        good_increment = int((self.get_min_shift_rpm() - self.get_power_band_start()) / 4)
        warning_increment = int((self.get_shift_alert_rpm() - self.get_min_shift_rpm()) / 4)
        alert_increment = int((self.get_rpm_limit() - self.get_shift_alert_rpm()) / 3)
        self.shift_triggers = [
            # tuplet (trigger rpm, led_colour, flash)
            {
                'rpm': self.get_power_band_start(), 'led': self.led_good, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_power_band_start() + (good_increment * 1), 'led': self.led_good, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_power_band_start() + (good_increment * 2), 'led': self.led_good, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_power_band_start() + (good_increment * 3), 'led': self.led_good, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_min_shift_rpm(), 'led': self.led_warning, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_min_shift_rpm() + (warning_increment * 1), 'led': self.led_warning, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_min_shift_rpm() + (warning_increment * 2), 'led': self.led_warning, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_min_shift_rpm() + (warning_increment * 3), 'led': self.led_warning, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_shift_alert_rpm(), 'led': self.led_alert, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_shift_alert_rpm() + (alert_increment * 1), 'led': self.led_alert, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_shift_alert_rpm() + (alert_increment * 2), 'led': self.led_alert, 'flash': False,
                'gear_color': self.default_gear_color
            },
            {
                'rpm': self.get_rpm_limit(), 'led': self.led_alert, 'flash': True,
                'gear_color': self.led_alert
            }
        ]

        self.pit_triggers = [
            # trigger kph, which blocks to light, block colour, flash, speed text color
            {
                'speed': self.get_pit_speed_limit() - 4, 'blks': [0, 4],
                'blk_color': self.led_good, 'flash': False, 'speed_color': self.default_speed_color
            },
            {
                'speed': self.get_pit_speed_limit() - 2, 'blks': [1, 3],
                'blk_color': self.led_warning, 'flash': False, 'speed_color': self.default_speed_color
            },
            {
                'speed': self.get_pit_speed_limit(), 'blks': [2],
                'blk_color': self.led_alert, 'flash': False, 'speed_color': self.led_alert
            },
            {
                'speed': self.get_pit_speed_limit() + 1, 'blks': [2],
                'blk_color': self.led_alert, 'flash': True, 'speed_color': self.led_alert
            }
        ]

    def read_config(self) -> None:
        # Read the configuration file
        self.config.read('config.ini')

    def get_test_mode(self) -> bool:
        if self.config.get('general', 'test_mode').upper() == 'TRUE':
            return True
        else:
            return False

    def get_log_level(self) -> int:
        return int(self.config.get('logging', 'log_level'))

    def get_pit_speed_limit(self) -> int:
        return int(self.config.get('pit', 'pit_speed_limit'))

    def set_pit_speed_limit(self, speed: int) -> None:
        self.config.set('pit', 'pit_speed_limit', str(speed))
        with open("config.ini", "w") as f:
            self.config.write(f)

    def get_fullscreen_state(self) -> bool:
        if self.config.get('general', 'fullscreen').upper() == 'TRUE':
            return True
        else:
            return False

    def set_fullscreen_state(self, state: bool) -> None:
        if state:
            self.config.set('general', 'fullscreen', 'true')
        else:
            self.config.set('general', 'fullscreen', 'false')
        with open("config.ini", "w") as f:
            self.config.write(f)

    def get_screen_width(self) -> int:
        return int(self.config.get('general', 'screen_width'))

    def get_screen_height(self) -> int:
        return int(self.config.get('general', 'screen_height'))

    def get_bg_color(self) -> str:
        return self.config.get('general', 'bg_color').replace("'", "")

    def get_base_font_size(self) -> int:
        return int(self.config.get('general', 'base_font_size'))

    def get_power_band_start(self) -> int:
        return int(self.config.get('shift', 'power_band_start'))

    def get_min_shift_rpm(self) -> int:
        return int(self.config.get('shift', 'min_shift_rpm'))

    def get_shift_alert_rpm(self) -> int:
        return int(self.config.get('shift', 'shift_alert_rpm'))

    def get_rpm_limit(self) -> int:
        return int(self.config.get('shift', 'rpm_limit'))

    def get_shift_screen_title(self) -> str:
        return self.config.get('shift', 'shift_screen_title').replace('"', '')

    def get_pit_screen_title(self) -> str:
        return self.config.get('pit', 'pit_screen_title').replace('"', '')

    def get_conf_screen_title(self) -> str:
        return self.config.get('config', 'config_screen_title').replace('"', '')

    def get_speed_correction_factor(self) -> float:
        return float(self.config.get('general', 'speed_correction_factor'))

    def get_gearing_factor(self):
        gearing_factor_list = self.config.get('general', 'gearing_factor').split()

        gearing_factor_values = [[number for number in range(2)] for _ in range(int(len(gearing_factor_list)/2))]

        j = 0
        for i, gearing_factor in enumerate(gearing_factor_list):
            if i % 2:
                gearing_factor_values[j][1] = int(gearing_factor)
                j += 1
            else:
                gearing_factor_values[j][0] = int(gearing_factor)

        return gearing_factor_values
