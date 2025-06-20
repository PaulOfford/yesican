# You can edit this file to customise your display.
# Be careful not to change the structure of the variables
# as this will cause program exceptions and the yesican won't run.
# Make a backup copy of this file before modifying it.
import configparser

import shared_memory
from constants import *


class Settings:
    config = configparser.ConfigParser()

    led_off_color = '#ffffff'
    default_gear_color = '#ffffff'
    default_speed_color = '#ffffff'
    default_blk_color = '#333333'

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

    def reload_config(self) -> None:
        self.read_config()

    def get_test_mode(self) -> bool:
        if self.config.get('general', 'test_mode').upper() == 'TRUE':
            return True
        else:
            return False

    def get_can_adapter(self) -> str:
        return self.config.get('general', 'can_adapter').replace('"', '')

    def get_can_send_adapter(self) -> str:
        return self.config.get('send', 'can_send_adapter').replace('"', '')

    def get_can_rate(self) -> int:
        return int(self.config.get('general', 'can_rate'))

    def get_log_level(self) -> int:
        return int(self.config.get('logging', 'log_level'))

    def get_pit_speed_limit(self) -> int:
        return int(self.config.get('pit', 'pit_speed_limit'))

    def set_pit_speed_limit(self, speed: int) -> None:
        self.config.set('pit', 'pit_speed_limit', str(speed))
        with open("config.ini", "w") as f:
            self.config.write(f)
        self.reload_config()

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

    def get_default_font_color(self) -> str:
        return self.config.get('general', 'default_font_color').replace("'", "")

    def get_base_font_size(self) -> int:
        return int(self.config.get('general', 'base_font_size')) * shared_memory.font_scale_factor

    def get_display_step_gpio_pin(self) -> int:
        return int(self.config.get('general', 'display_step_gpio_pin'))

    def get_power_band_start(self) -> int:
        return int(self.config.get('shift', 'power_band_start'))

    def get_min_shift_rpm(self) -> int:
        return int(self.config.get('shift', 'min_shift_rpm'))

    def get_shift_alert_rpm(self) -> int:
        return int(self.config.get('shift', 'shift_alert_rpm'))

    def get_rpm_limit(self) -> int:
        return int(self.config.get('shift', 'rpm_limit'))

    def get_page_title(self, page_id: int) -> str:

        if page_id == DM_GEAR_SHIFT_INDICATOR:
            title = self.config.get('shift', 'page_title').replace('"', '')
        elif page_id == DM_PIT_SPEED_INDICATOR:
            title = self.config.get('pit', 'page_title').replace('"', '')
        elif page_id == DM_BRAKE_TRACE_PLOT:
            title = self.config.get('brakes', 'page_title').replace('"', '')
        elif page_id == DM_FUEL_BURN:
            title = self.config.get('fuel', 'page_title').replace('"', '')
        elif page_id == DM_CONFIGURATION:
            title = self.config.get('config', 'page_title').replace('"', '')
        else:
            title = "PAGE_ID UNKNOWN"

        return title

    def get_shift_screen_title(self) -> str:
        return self.config.get('shift', 'shift_screen_title').replace('"', '')

    def get_pit_screen_title(self) -> str:
        return self.config.get('pit', 'pit_screen_title').replace('"', '')

    def get_pit_switch_gpio_pin(self) -> int:
        return int(self.config.get('pit', 'pit_switch_gpio_pin'))

    def get_brake_trace_title(self) -> str:
        return self.config.get('brakes', 'brake_trace_title').replace('"', '')

    def get_plot_count(self) -> int:
        return int(self.config.get('brakes', 'plot_count'))

    def get_pressure_multiplier(self) -> float:
        return float(self.config.get('brakes', 'pressure_multiplier'))

    def get_conf_screen_title(self) -> str:
        return self.config.get('config', 'config_screen_title').replace('"', '')

    def get_canbus_codes(self) -> str:
        return self.config.get('general', 'canbus_codes').replace('"', '')

    def get_speed_correction_factor(self) -> float:
        return float(self.config.get('general', 'speed_correction_factor'))

    def set_speed_correction_factor(self, factor: float) -> None:
        self.config.set('general', 'speed_correction_factor', str(factor))
        with open("config.ini", "w") as f:
            self.config.write(f)
        self.reload_config()

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

    def get_brake_tone_volume(self):
        return int(self.config.get('brakes', 'brake_tone_volume'))

    def set_brake_tone_volume(self, volume: int) -> None:
        self.config.set('brakes', 'brake_tone_volume', str(volume))
        with open("config.ini", "w") as f:
            self.config.write(f)
        self.reload_config()

    def get_race_duration(self) -> int:
        return int(self.config.get('fuel', 'race_duration'))

    def set_race_duration(self, duration: int) -> None:
        self.config.set('fuel', 'race_duration', str(duration))
        with open("config.ini", "w") as f:
            self.config.write(f)
        self.reload_config()

    def get_default_consumption_lpm(self) -> float:
        return float(self.config.get('fuel', 'default_consumption_lpm'))

    def set_default_consumption_lpm(self, factor: float) -> None:
        self.config.set('fuel', 'default_consumption_lpm', str(factor))
        with open("config.ini", "w") as f:
            self.config.write(f)
        self.reload_config()
