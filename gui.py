import os
import pathlib
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
    shared_memory.desired_mode = (shared_memory.desired_mode + 1) % 3


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
    config_button = None

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

    def update_rpm_gauge(self):
        if shared_memory.eng_rpm > 7100 or shared_memory.eng_rpm < 850:
            shared_memory.eng_rpm = 850
        else:
            shared_memory.eng_rpm += 250
        self.sv_rpm.set(str(shared_memory.eng_rpm))

    def update_shift_lights(self):
        for i, light in enumerate(self.led):
            self.my_canvas.itemconfigure(light, fill=self.led_color(i, shared_memory.eng_rpm))

    def update_gear_gauge(self):
        self.sv_gear.set(str(shared_memory.pre_calc_gear))
        self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))

    def process_updates(self):
        self.update_rpm_gauge()
        self.update_shift_lights()
        self.update_gear_gauge()
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

        # place the config button
        # img_file_name = r"images\settings-cogwheel-button-white.png"
        # current_dir = pathlib.Path(__file__).parent.resolve()  # current directory
        # img_path = os.path.join(current_dir, img_file_name)  # join with your image's file name
        # cog_icon = tk.PhotoImage(file=img_path)
        # self.config_button = tk.Button(
        #     self, image=cog_icon, width=48, height=48, bg="red", bd=0
        # )

        self.config_button = tk.Button(self, text='Next', command=next_display)

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
        self.config_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()

        # self.my_root.after(200, self.process_updates)
        # self.my_root.mainloop()


class GuiPitSpeed(tk.Frame):

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
    config_button = None

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

    def update_rpm_gauge(self):
        if shared_memory.eng_rpm > 7100 or shared_memory.eng_rpm < 850:
            shared_memory.eng_rpm = 850
        else:
            shared_memory.eng_rpm += 250
        self.sv_rpm.set(str(shared_memory.eng_rpm))

    def update_shift_lights(self):
        for i, light in enumerate(self.led):
            self.my_canvas.itemconfigure(light, fill=self.led_color(i, shared_memory.eng_rpm))

    def update_gear_gauge(self):
        self.sv_gear.set(str(shared_memory.pre_calc_gear))
        self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))

    def process_updates(self):
        self.update_rpm_gauge()
        self.update_shift_lights()
        self.update_gear_gauge()
        self.after(250, self.process_updates)

    def render_screen(self):
        self.configure(bg=self.settings.bg_color, borderwidth=0)

        font_title = font.Font(family='Ariel', size=(int(self.settings.base_font_size/4)), weight='normal')
        font_gear = font.Font(family='Ariel', size=int(self.settings.base_font_size*1.1), weight='normal')

        # widgets
        self.screen_title = tk.Label(
            self, text=self.settings.pit_screen_title,
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

        # place the config button
        # img_file_name = r"images\settings-cogwheel-button-white.png"
        # current_dir = pathlib.Path(__file__).parent.resolve()  # current directory
        # img_path = os.path.join(current_dir, img_file_name)  # join with your image's file name
        # cog_icon = tk.PhotoImage(file=img_path)
        # self.config_button = tk.Button(
        #     self, image=cog_icon, width=48, height=48, bg="red", bd=0
        # )

        self.config_button = tk.Button(self, text='Next', command=next_display)

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
        self.config_button.grid(row=3, column=2, sticky='se', padx=10, pady=10)

        # pack this frame with the content above
        self.pack()

        # self.my_root.after(200, self.process_updates)
        # self.my_root.mainloop()


