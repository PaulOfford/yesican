from typing import Union
import tkinter as tk
import tkinter.font as font
import shared_memory

from _version import __version__
from settings import *


def create_circle(x, y, r, canvas, color):  # center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)


def next_display() -> None:
    shared_memory.desired_mode = (shared_memory.desired_mode + 1) % shared_memory.no_of_modes


def quit_yesican():
    exit(0)


class GuiBlank(tk.Frame):

    settings = Settings()

    def __init__(self, parent):
        super().__init__(parent)
        self.render_screen()

    def render_screen(self):
        self.pack()


class GuiGearShift(tk.Frame):

    settings = Settings()

    # my_root = None
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

    def led_color(self, led_index: int, rpm: int) -> str:
        color = self.settings.led_off_color  # this is the default if the light is not on

        trigger = self.settings.shift_triggers[led_index]
        if rpm >= trigger['rpm']:
            color = trigger['led']

        return color

    def populate_shift_leds(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        radius = self.settings.led_radius
        self.my_canvas = tk.Canvas(
            container, bg=self.settings.bg_color,
            height=(4 * radius), width=self.settings.screen_width,
            border=0, highlightthickness=0
        )
        offset = 2.5 * radius
        xpos = (self.settings.screen_width / 2) - (5 * offset)
        ypos = 2 * radius

        for i in range(0, self.settings.no_of_leds):
            self.led.append(
                create_circle(xpos + (i * offset), ypos, radius, self.my_canvas, self.settings.led_off_color)
            )

        return self.my_canvas

    def gear_color(self, rpm: int) -> str:
        gear_text_color = self.settings.default_gear_color
        for trigger in self.settings.shift_triggers:
            if rpm >= trigger['rpm']:
                gear_text_color = trigger['gear_color']
        return gear_text_color

    @staticmethod
    def sim_rpm():
        if shared_memory.eng_rpm > 8000 or shared_memory.eng_rpm < 850:
            shared_memory.eng_rpm = 850
        else:
            shared_memory.eng_rpm += 250

    def update_rpm_gauge(self):
        self.sv_rpm.set(str(shared_memory.eng_rpm))

    def update_shift_lights(self):
        for i, light in enumerate(self.led):
            self.my_canvas.itemconfigure(light, fill=self.led_color(i, shared_memory.eng_rpm))

        # this code block handles flashing
        shared_memory.flash_window = False  # default is to not flash the display
        for trigger in reversed(self.settings.shift_triggers):
            if shared_memory.eng_rpm >= trigger['rpm']:
                shared_memory.flash_window = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

    def update_gear_gauge(self):
        self.sv_gear.set(str(shared_memory.pre_calc_gear))
        self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))

    def process_updates(self):
        if shared_memory.current_mode == 0:
            self.sim_rpm()
            self.update_shift_lights()
            self.update_gear_gauge()
            self.update_rpm_gauge()
        self.after(250, self.process_updates)

    def render_screen(self):
        self.configure(bg=self.settings.bg_color, borderwidth=0)

        font_title = font.Font(family='Ariel', size=(int(self.settings.base_font_size/4)), weight='normal')
        font_gear = font.Font(family='Ariel', size=int(self.settings.base_font_size*1.1), weight='normal')

        # widgets
        self.screen_title = tk.Label(
            self, text=self.settings.shift_screen_title,
            width=20, pady=12, fg='white', bg=self.settings.bg_color, font=font_title
        )
        self.shift_lights = self.populate_shift_leds(container=self)

        self.gear_value = tk.Label(
            self, textvariable=self.sv_gear,
            fg=self.gear_color(shared_memory.eng_rpm), bg=self.settings.bg_color, font=font_gear
        )

        self.sv_rpm.set(str(shared_memory.eng_rpm))
        self.rpm_label = tk.Label(
            self, textvariable=self.sv_rpm, fg="white", bg=self.settings.bg_color, font=font_title
        )

        self.next_button = tk.Button(self, text='Next', command=next_display)

        # define grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        self.screen_title.grid(row=0, column=0, columnspan=3)
        self.shift_lights.grid(row=1, column=0, columnspan=3)
        self.gear_value.grid(row=2, column=0, columnspan=3)
        self.rpm_label.grid(row=3, column=0, sticky='sw', padx=5, pady=5)
        self.next_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()

        # self.my_root.after(200, self.process_updates)
        # self.my_root.mainloop()


class GuiPitSpeed(tk.Frame):

    settings = Settings()

    # my_root = None
    my_canvas = None

    # this will be a StringVar that we will use as a textvariable in a Label object
    sv_speed = None

    speed_value = None
    speed_color = settings.default_speed_color

    speed_blocks = None
    blk = []

    def __init__(self, parent):
        super().__init__(parent)
        self.sv_speed = tk.StringVar()
        self.render_screen()
        self.process_updates()

    def create_gauge(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        radius = self.settings.led_radius
        self.my_canvas = tk.Canvas(
            container, bg=self.settings.bg_color,
            height=(4 * radius), width=self.settings.screen_width,
            border=0, highlightthickness=0
        )

        blk_width = 80
        blk_height = 20
        xstart = (self.settings.screen_width / 2) - (2.5 * blk_width)
        ypos = 1 * blk_height

        for i in range(0, 5):
            xpos = xstart + (i * blk_width)
            self.blk.append(
                self.my_canvas.create_rectangle(
                    xpos, ypos, xpos + blk_width, ypos + blk_height, outline=self.settings.bg_color
                )
            )
            self.my_canvas.itemconfigure(self.blk[i], fill=self.settings.default_blk_color)

        return self.my_canvas

    @staticmethod
    def sim_speed():
        if shared_memory.speed > 52 or shared_memory.speed < 42:
            shared_memory.speed = 42
        else:
            shared_memory.speed += 1

    def update_speed_gauge(self):
        self.sv_speed.set(str(shared_memory.speed))
        self.speed_value.configure(fg=self.speed_color)

    def update_speed_blocks(self):
        # reset all the speed blocks
        for i, blk in enumerate(self.blk):
            self.my_canvas.itemconfigure(blk, fill=self.settings.default_blk_color)

        self.speed_color = self.settings.default_speed_color  # set speed value color to default
        for trigger in reversed(self.settings.pit_triggers):
            if shared_memory.speed >= trigger['speed']:
                for blk_offset in trigger['blks']:
                    self.my_canvas.itemconfigure(self.blk[blk_offset], fill=trigger['blk_color'])
                # set the speed gauge color
                self.speed_color = trigger['speed_color']
                # now we've done that we don't want to look for further pit_triggers matches
                break

        # this code block handles flashing
        shared_memory.flash_window = False  # default is to not flash the display
        for trigger in reversed(self.settings.pit_triggers):
            if shared_memory.speed >= trigger['speed']:
                shared_memory.flash_window = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

    def process_updates(self):
        # we only want to mess with the display if it is top of the stack
        if shared_memory.current_mode == 1:
            self.sim_speed()
            self.update_speed_blocks()
            self.update_speed_gauge()
        self.after(500, self.process_updates)

    def render_screen(self):
        self.configure(bg=self.settings.bg_color, borderwidth=0)

        font_title = font.Font(family='Ariel', size=(int(self.settings.base_font_size/4)), weight='normal')
        font_gear = font.Font(family='Ariel', size=int(self.settings.base_font_size*1.1), weight='normal')

        # widgets
        screen_title = tk.Label(
            self, text=self.settings.pit_screen_title,
            width=20, pady=12, fg='white', bg=self.settings.bg_color, font=font_title
        )
        self.speed_blocks = self.create_gauge(container=self)

        self.speed_value = tk.Label(
            self, textvariable=self.sv_speed,
            fg=self.speed_color, bg=self.settings.bg_color, font=font_gear
        )

        next_button = tk.Button(self, text='Next', command=next_display)

        # define grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)

        screen_title.grid(row=0, column=0, columnspan=3)
        self.speed_blocks.grid(row=1, column=0, columnspan=3)
        self.speed_value.grid(row=2, column=0, columnspan=3)
        next_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()


class GuiConfig(tk.Frame):

    settings = Settings()

    # speed_correction_factor equals real speed / dashboard (ECU) speed
    # and corrects for the situation where the radius of the fitted tyres
    # differs from that of the original tyres
    speed_correction_factor = 151 / 160

    speed_limit = 50  # kph - pit lane speed limit - default is 50

    # gearing_factor is used in the calculation of current gear from corrected speed and rpm
    # each entry represents a gear (starting from Neutral) has min and max kph per 1000 rpm
    # set min as low as possible without overlapping with the previous gear to accommodate wheel spin
    # default is BMW 116i E87 5 speed with Nankang NS-2R tyres
    gearing_factor = [(0, 0), (1, 8), (9, 12), (13, 18), (19, 25), (26, 100)]

    speed_blocks = None
    blk = []

    def __init__(self, parent):
        super().__init__(parent)
        self.sv_speed = tk.StringVar()
        self.render_screen()

    def render_screen(self):
        self.configure(bg=self.settings.bg_color, borderwidth=0)

        font_title = font.Font(family='Ariel', size=(int(self.settings.base_font_size/4)), weight='normal')
        font_inputs = font.Font(family='Ariel', size=int(self.settings.base_font_size*0.12), weight='normal')

        # widgets
        screen_title = tk.Label(
            self, text=self.settings.config_screen_title,
            width=self.settings.screen_width, pady=12, fg='white', bg=self.settings.bg_color, font=font_title
        )

        speed_limit = tk.Label(
            self, text="Pit Lane Speed Limit (kph):",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        fullscreen = tk.Label(
            self, text="Fullscreen Mode:",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        version = tk.Label(
            self, text=__version__,
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank3 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank4 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank5 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank6 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank7 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        blank8 = tk.Label(
            self, text=" ",
            fg='white', bg=self.settings.bg_color, font=font_inputs
        )

        quit_button = tk.Button(self, text='Quit', command=quit_yesican)
        next_button = tk.Button(self, text='Next', command=next_display)

        # define grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)

        screen_title.grid(row=0, column=0, columnspan=3, padx=10)
        speed_limit.grid(row=1, column=0, sticky='w', padx=10, pady=5)
        fullscreen.grid(row=2, column=0, sticky='w', padx=10, pady=5)
        blank3.grid(row=3, column=0, sticky='w', padx=10, pady=5)
        blank4.grid(row=4, column=0, sticky='w', padx=10, pady=5)
        blank5.grid(row=5, column=0, sticky='w', padx=10, pady=5)
        blank6.grid(row=6, column=0, sticky='w', padx=10, pady=5)
        blank7.grid(row=7, column=0, sticky='w', padx=10, pady=5)
        blank8.grid(row=8, column=0, sticky='w', padx=10, pady=5)
        quit_button.grid(row=9, column=0, sticky='sw', padx=10, pady=10)
        # version.grid(row=3, column=1)
        next_button.grid(row=9, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()
