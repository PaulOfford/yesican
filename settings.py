# You can edit this file to customise your display.
# Be careful not to change the structure of the variables
# as this will cause program exceptions and the yesican won't run.
# Make a backup copy of this file before modifying it.
import configparser

class Settings:
    screen_width = 480
    screen_height = 320
    fullscreen = 1  # 0 = off, 1 = on

    base_font_size = 96
    bg_color = "#595959"
    led_off_color = 'white'
    default_gear_color = 'white'
    default_speed_color = default_gear_color
    default_blk_color = bg_color

    led_radius = 16
    led_clr = ["#00FF00", "yellow", "red"]
    no_of_leds = 11

    shift_screen_title = "Gear Shift"
    shift_triggers = [
        # tuplet (trigger rpm, led_colour, flash)
        {'rpm': 4500, 'led': led_clr[0], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 5000, 'led': led_clr[0], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 5500, 'led': led_clr[0], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6000, 'led': led_clr[0], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6500, 'led': led_clr[1], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6575, 'led': led_clr[1], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6650, 'led': led_clr[1], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6725, 'led': led_clr[1], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6800, 'led': led_clr[2], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6866, 'led': led_clr[2], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 6932, 'led': led_clr[2], 'flash': False, 'gear_color': default_gear_color},
        {'rpm': 7000, 'led': led_clr[2], 'flash': True, 'gear_color': led_clr[2]}
    ]

    pit_screen_title = "Pit Speed"
    pit_speed_limit = 50
    pit_triggers = [
        # trigger kph, which blocks to light, block colour, flash, speed text color
        {
            'speed': pit_speed_limit - 4, 'blks': [0, 4],
            'blk_color': led_clr[0], 'flash': False, 'speed_color': default_speed_color
        },
        {
            'speed': pit_speed_limit - 2, 'blks': [1, 3],
            'blk_color': led_clr[1], 'flash': False, 'speed_color': default_speed_color
        },
        {
            'speed': pit_speed_limit, 'blks': [2],
            'blk_color': led_clr[2], 'flash': False, 'speed_color': led_clr[2]
        },
        {
            'speed': pit_speed_limit + 1, 'blks': [2],
            'blk_color': led_clr[2], 'flash': True, 'speed_color': led_clr[2]
        }
    ]

    config_screen_title = "Configuration"

    def read_config(self) -> None:
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        # Read the configuration file
        config.read('config.ini')

        # Access values from the configuration file
        self.screen_width = config.get('General', 'screen_width')
        self.screen_height = config.get('General', 'screen_height')
        self.fullscreen = config.get('General', 'fullscreen')
        self.base_font_size = config.get('General', 'base_font_size')
        self.bg_color = config.get('General', 'bg_color')

        return

    def set_fullscreen(self):
        self.fullscreen = 1

