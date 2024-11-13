from typing import Union
import tkinter as tk
import tkinter.font as font

import shared_memory

from yesican import yesican_shutdown
from _version import __version__
from my_logger import microsec_message
from constants import *


def create_circle(x, y, r, canvas, color):  # center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)


def next_display() -> None:
    shared_memory.flash_window = False
    shared_memory.desired_mode = (shared_memory.desired_mode + 1) % shared_memory.no_of_modes


def round_to_fifty(number: int) -> int:
    return 50 * round(number/50)

class GuiBlank(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.render_screen()

    def render_screen(self):
        self.pack()


class GuiGearShift(tk.Frame):

    my_canvas = None

    sv_rpm = None
    sv_gear = None

    gear_value = None

    screen_title = None
    shift_lights = None
    led = []
    rpm_label = None
    next_button = None

    def __init__(self, parent):
        super().__init__(parent)
        self.sv_rpm = tk.StringVar()
        self.sv_gear = tk.StringVar()
        self.render_screen()
        self.process_updates()

    @staticmethod
    def led_color(led_index: int, rpm: int) -> str:
        color = shared_memory.settings.led_off_color  # this is the default if the light is not on

        trigger = shared_memory.settings.shift_triggers[led_index]
        if rpm >= trigger['rpm']:
            color = trigger['led']

        return color

    def populate_shift_leds(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        radius = shared_memory.settings.led_radius
        self.my_canvas = tk.Canvas(
            container, bg=shared_memory.settings.get_bg_color(),
            height=(4 * radius), width=shared_memory.settings.get_screen_width(),
            border=0, highlightthickness=0
        )
        offset = 2.5 * radius
        xpos = int((shared_memory.settings.get_screen_width() / 2) - (5 * offset))
        ypos = 2 * radius

        for i in range(0, shared_memory.settings.no_of_leds):
            self.led.append(
                create_circle(xpos + (i * offset), ypos, radius, self.my_canvas, shared_memory.settings.led_off_color)
            )

        return self.my_canvas

    @staticmethod
    def gear_color(rpm: int) -> str:
        gear_text_color = shared_memory.settings.default_gear_color
        for trigger in shared_memory.settings.shift_triggers:
            if rpm >= trigger['rpm']:
                gear_text_color = trigger['gear_color']
        return gear_text_color

    def update_rpm_gauge(self):
        self.sv_rpm.set(str(round_to_fifty(shared_memory.eng_rpm)))

    def update_shift_lights(self):
        for i, light in enumerate(self.led):
            self.my_canvas.itemconfigure(light, fill=self.led_color(i, shared_memory.eng_rpm))

        # this code block handles flashing
        shared_memory.flash_window = False  # default is to not flash the display
        for trigger in reversed(shared_memory.settings.shift_triggers):
            if shared_memory.eng_rpm >= trigger['rpm']:
                shared_memory.flash_window = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

    def update_gear_gauge(self):
        if shared_memory.pre_calc_gear == 0:
            displayed_gear = 'N'
        else:
            displayed_gear = str(shared_memory.pre_calc_gear)
        self.sv_gear.set(displayed_gear)
        self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))

    def process_updates(self):
        if shared_memory.current_mode == 0:
            microsec_message(4, "Gear shift display update start")
            self.update_shift_lights()
            self.update_gear_gauge()
            self.update_rpm_gauge()
            microsec_message(4, "Gear shift display update end")

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(50, self.process_updates)
        else:
            yesican_shutdown()

    def render_screen(self):
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)

        font_title = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())/4), weight='normal'
        )
        font_gear = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*1.1), weight='normal'
        )

        # widgets
        self.screen_title = tk.Label(
            self, text=shared_memory.settings.get_shift_screen_title(),
            width=20, pady=12, fg='white', bg=shared_memory.settings.get_bg_color(), font=font_title
        )
        self.shift_lights = self.populate_shift_leds(container=self)

        self.gear_value = tk.Label(
            self, textvariable=self.sv_gear,
            fg=self.gear_color(shared_memory.eng_rpm), bg=shared_memory.settings.get_bg_color(), font=font_gear
        )

        self.sv_rpm.set(str(shared_memory.eng_rpm))
        self.rpm_label = tk.Label(
            self, textvariable=self.sv_rpm, fg="white", bg=shared_memory.settings.get_bg_color(), font=font_title
        )

        self.next_button = tk.Button(self, text='Next', command=next_display)

        # define grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        shared_memory.root.update()
        self.rowconfigure(0, weight=1, minsize=shared_memory.root.winfo_height() * 0.15)  # 10% for title
        self.rowconfigure(1, weight=1, minsize=shared_memory.root.winfo_height() * 0.25)  # 25% for LEDs
        self.rowconfigure(2, weight=1, minsize=shared_memory.root.winfo_height() * 0.45)  # 50% for gear number
        self.rowconfigure(3, weight=1, minsize=shared_memory.root.winfo_height() * 0.15)  # 15% for footer

        self.screen_title.grid(row=0, column=0, columnspan=3)
        self.shift_lights.grid(row=1, column=0, columnspan=3)
        self.gear_value.grid(row=2, column=0, columnspan=3)
        self.rpm_label.grid(row=3, column=0, sticky='sw', padx=5, pady=5)
        self.next_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()


class GuiPitSpeed(tk.Frame):

    my_canvas = None

    # this will be a StringVar that we will use as a textvariable in a Label object
    sv_speed = None

    speed_value = None
    speed_color = shared_memory.settings.default_speed_color

    speed_blocks = None
    blk = []

    def __init__(self, parent):
        super().__init__(parent)
        self.sv_speed = tk.StringVar()
        self.render_screen()
        self.process_updates()

    def create_gauge(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        radius = shared_memory.settings.led_radius
        self.my_canvas = tk.Canvas(
            container, bg=shared_memory.settings.get_bg_color(),
            height=(4 * radius), width=shared_memory.settings.get_screen_width(),
            border=0, highlightthickness=0
        )

        blk_width = 80
        blk_height = 20
        xstart = (shared_memory.settings.get_screen_width() / 2) - (2.5 * blk_width)
        ypos = 1 * blk_height

        for i in range(0, 5):
            xpos = xstart + (i * blk_width)
            self.blk.append(
                self.my_canvas.create_rectangle(
                    xpos, ypos, xpos + blk_width, ypos + blk_height, outline=shared_memory.settings.get_bg_color()
                )
            )
            self.my_canvas.itemconfigure(self.blk[i], fill=shared_memory.settings.default_blk_color)

        return self.my_canvas

    def update_speed_gauge(self):
        self.sv_speed.set(str(shared_memory.speed))
        self.speed_value.configure(fg=self.speed_color)

    def update_speed_blocks(self):
        # reset all the speed blocks
        for i, blk in enumerate(self.blk):
            self.my_canvas.itemconfigure(blk, fill=shared_memory.settings.default_blk_color)

        self.speed_color = shared_memory.settings.default_speed_color  # set speed value color to default
        for trigger in reversed(shared_memory.settings.pit_triggers):
            if shared_memory.speed >= trigger['speed']:
                for blk_offset in trigger['blks']:
                    self.my_canvas.itemconfigure(self.blk[blk_offset], fill=trigger['blk_color'])
                # set the speed gauge color
                self.speed_color = trigger['speed_color']
                # now we've done that we don't want to look for further pit_triggers matches
                break

        # this code block handles flashing
        shared_memory.flash_window = False  # default is to not flash the display
        for trigger in reversed(shared_memory.settings.pit_triggers):
            if shared_memory.speed >= trigger['speed']:
                shared_memory.flash_window = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

    def process_updates(self):
        # we only want to mess with the display if it is top of the stack
        if shared_memory.current_mode == 1:
            microsec_message(4, "Pit speed display update start")
            # self.sim_speed()
            self.update_speed_blocks()
            self.update_speed_gauge()
            microsec_message(4, "Pit speed display update end")
        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(50, self.process_updates)
        else:
            yesican_shutdown()

    def render_screen(self):
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)

        font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()/4), weight='normal'
        )
        font_gear = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()*1.1), weight='normal'
        )

        # widgets
        screen_title = tk.Label(
            self, text=shared_memory.settings.get_pit_screen_title(),
            width=20, pady=12, fg='white', bg=shared_memory.settings.get_bg_color(), font=font_title
        )
        self.speed_blocks = self.create_gauge(container=self)

        self.speed_value = tk.Label(
            self, textvariable=self.sv_speed,
            fg=self.speed_color, bg=shared_memory.settings.get_bg_color(), font=font_gear
        )

        next_button = tk.Button(self, text='Next', command=next_display)

        # define grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        shared_memory.root.update()
        self.rowconfigure(0, weight=1, minsize=shared_memory.root.winfo_height() * 0.15)
        self.rowconfigure(1, weight=1, minsize=shared_memory.root.winfo_height() * 0.25)
        self.rowconfigure(2, weight=1, minsize=shared_memory.root.winfo_height() * 0.45)
        self.rowconfigure(3, weight=1, minsize=shared_memory.root.winfo_height() * 0.15)

        screen_title.grid(row=0, column=0, columnspan=3)
        self.speed_blocks.grid(row=1, column=0, columnspan=3)
        self.speed_value.grid(row=2, column=0, columnspan=3)
        next_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()


class GuiConfig(tk.Frame):

    pit_speed = None  # StringVar
    speed_correction_factor = None  # StringVar
    fs_status = None  # IntVar

    speed_blocks = None
    blk = []

    def __init__(self, parent):
        super().__init__(parent)
        self.pit_speed = tk.StringVar()
        self.fs_status = tk.IntVar()
        self.render_screen()

    def update_config(self) -> None:
        shared_memory.settings.set_pit_speed_limit(self.pit_speed.get())
        shared_memory.settings.set_speed_correction_factor(self.speed_correction_factor.get())
        pass

    def next_display(self) -> None:
        self.update_config()
        shared_memory.desired_mode = (shared_memory.desired_mode + 1) % shared_memory.no_of_modes

    def quit_yesican(self):
        self.update_config()
        shared_memory.set_run_state(RUN_STATE_PENDING_SHUTDOWN)
        yesican_shutdown()

    def render_screen(self):
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)

        font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()/4), weight='normal'
        )
        font_inputs = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()*0.12), weight='normal'
        )

        # widgets
        screen_title = tk.Label(
            self, text=shared_memory.settings.get_conf_screen_title(),
            width=shared_memory.settings.get_screen_width(), pady=12,
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_title
        )

        speed_limit = tk.Label(
            self, text="Pit Lane Speed Limit (kph):",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        self.pit_speed = tk.StringVar()
        self.pit_speed.set(str(shared_memory.settings.get_pit_speed_limit()))
        speed_box = tk.Entry(self, textvariable=self.pit_speed)

        correction_factor_label = tk.Label(
            self, text="Speed Correction Factor:",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        self.speed_correction_factor = tk.StringVar()
        self.speed_correction_factor.set(str(shared_memory.settings.get_speed_correction_factor()))
        correction_factor = tk.Entry(self, textvariable=self.speed_correction_factor)

        fullscreen = tk.Label(
            self, text="Fullscreen Mode:",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        self.fs_status = tk.IntVar()
        self.fs_status.set(shared_memory.settings.get_fullscreen_state())
        fullscreen_check_box = tk.Checkbutton(
            self, variable=self.fs_status, bg=shared_memory.settings.get_bg_color(),
            command=lambda: shared_memory.settings.set_fullscreen_state(self.fs_status.get())
        )

        version = tk.Label(
            self, text=__version__,
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        blank4 = tk.Label(
            self, text=" ",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        blank5 = tk.Label(
            self, text=" ",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        blank6 = tk.Label(
            self, text=" ",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        blank7 = tk.Label(
            self, text=" ",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        blank8 = tk.Label(
            self, text=" ",
            fg='white', bg=shared_memory.settings.get_bg_color(), font=font_inputs
        )

        quit_button = tk.Button(self, text='Quit', command=self.quit_yesican)
        next_button = tk.Button(self, text='Next', command=self.next_display)

        # define grid
        self.columnconfigure(0, weight=1, minsize=int(shared_memory.settings.get_screen_width()/3))
        self.columnconfigure(1, weight=1, minsize=int(shared_memory.settings.get_screen_width()/3))
        self.columnconfigure(2, weight=1, minsize=int(shared_memory.settings.get_screen_width()/3))
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)

        screen_title.grid(row=0, column=0, columnspan=3, padx=10)

        speed_limit.grid(row=1, column=0, sticky='e', padx=10, pady=5)
        speed_box.grid(row=1, column=1, sticky='w', padx=10, pady=5)

        correction_factor_label.grid(row=2, column=0, sticky='e', padx=10, pady=5)
        correction_factor.grid(row=2, column=1, sticky='w', padx=10, pady=5)

        fullscreen.grid(row=3, column=0, sticky='e', padx=10, pady=5)
        fullscreen_check_box.grid(row=3, column=1, sticky='w', padx=10, pady=5)

        blank4.grid(row=4, column=0, sticky='w', padx=10, pady=5)
        blank5.grid(row=5, column=0, sticky='w', padx=10, pady=5)
        blank6.grid(row=6, column=0, sticky='w', padx=10, pady=5)
        blank7.grid(row=7, column=0, sticky='w', padx=10, pady=5)
        quit_button.grid(row=9, column=0, sticky='sw', padx=10, pady=10)
        version.grid(row=9, column=1, sticky='ew', padx=10, pady=10)
        next_button.grid(row=9, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()
