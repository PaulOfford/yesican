# You can edit this file to customise your display.
# Be careful not to change the structure of the variables
# as this will cause program exceptions and the yesican won't run.
# Make a backup copy of this file before modifying it.

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
    pit_triggers = [
        # trigger kph, which blocks to light, block colour, flash, speed text color
        {'speed': 46, 'blks': [0, 4], 'blk_color': led_clr[0], 'flash': False, 'speed_color': default_speed_color},
        {'speed': 48, 'blks': [1, 3], 'blk_color': led_clr[1], 'flash': False, 'speed_color': default_speed_color},
        {'speed': 50, 'blks': [2], 'blk_color': led_clr[2], 'flash': False, 'speed_color': led_clr[2]},
        {'speed': 51, 'blks': [2], 'blk_color': led_clr[2], 'flash': True, 'speed_color': led_clr[2]}
    ]

    config_screen_title = "Configuration"
