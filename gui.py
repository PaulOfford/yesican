import tkinter
import time
from typing import Union
import tkinter as tk
import tkinter.font as font
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pygame
from array import (array)
from pygame.mixer import (Sound, get_init, pre_init)


import shared_memory

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from yesican import MainWindow
from _version import __version__
from my_logger import microsec_message
from constants import *


def create_circle(x, y, r, canvas, color):  # center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)


def round_to_fifty(number: int) -> int:
    return 50 * round(number/50)


def convert_sss_to_mm_ss(seconds: int) -> str:
    if seconds < 0:
        seconds *= -1
        neg_symbol = "-"
    else:
        neg_symbol = ""

    mm = int(seconds/60)
    ss = int(seconds - (mm * 60))

    return f"{neg_symbol}{mm:02}:{ss:02}"


def format_outer_frame(outer_frame: tk.Frame, frame_height: int):
    outer_frame.columnconfigure(0, weight=1)
    outer_frame.rowconfigure(0, weight=1, minsize=frame_height * 0.15)  # 15% for header
    outer_frame.rowconfigure(1, weight=1, minsize=frame_height * 0.70)  # 70% for body
    outer_frame.rowconfigure(2, weight=1, minsize=frame_height * 0.15)  # 15% for footer


def build_header(parent: tk.Frame) -> tk.Frame:
    header = tk.Frame(parent)
    header.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
    header.columnconfigure(0, weight=1)
    header.rowconfigure(0, weight=1)
    return header


def build_footer(parent: tk.Frame) -> tk.Frame:
    footer = tk.Frame(parent)
    # Builds a 3 x 1 grid
    footer.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
    footer.columnconfigure(0, weight=1, minsize=int(footer.winfo_width() * 0.4))
    footer.columnconfigure(1, weight=1, minsize=int(footer.winfo_width() * 0.2))
    footer.columnconfigure(2, weight=1, minsize=int(footer.winfo_width() * 0.4))
    footer.rowconfigure(0, weight=1)
    return footer


def get_header_frame(parent: tk.Frame, page_title: str, width: int) -> tk.Frame:
    font_title = font.Font(
        family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 4), weight='normal'
    )
    header = build_header(parent)
    screen_title = tk.Label(
        header, text=page_title, width=width,
        pady=12, fg=shared_memory.settings.get_default_font_color(),
        bg=shared_memory.settings.get_bg_color(), font=font_title
    )
    screen_title.grid(row=0, column=0, sticky='ew')
    return header


class GuiBlank(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent)
        self.render_screen()

    def render_screen(self):
        self.pack()


class GuiGearShift(tk.Frame):
    main_window = None
    my_canvas = None
    flash_display = False
    visible = True

    sv_rpm = None
    sv_gear = None
    sv_clutch = None

    gear_value = None

    font_title = None
    font_gear = None

    screen_title = None
    shift_lights = None
    led = []
    rpm_label = None
    next_button = None

    def __init__(self, this_window: MainWindow, parent: tk.Frame):
        super().__init__(parent)
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.main_window = this_window

        self.sv_rpm = tk.StringVar()
        self.sv_gear = tk.StringVar()
        self.sv_clutch = tk.StringVar()

        self.font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 4), weight='normal'
        )
        self.font_gear = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*1.1), weight='normal'
        )
        self.font_inputs = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()*0.12), weight='normal'
        )

        self.render_screen(parent)
        self.process_updates()

    @staticmethod
    def led_color(led_index: int, rpm: int) -> str:
        color = shared_memory.settings.led_off_color  # this is the default if the light is not on

        trigger = shared_memory.settings.shift_triggers[led_index]
        if rpm >= trigger['rpm']:
            color = trigger['led']

        return color

    def populate_shift_leds(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        width = container.winfo_reqwidth()
        radius = shared_memory.settings.led_radius
        self.my_canvas = tk.Canvas(
            container, bg=shared_memory.settings.get_bg_color(),
            height=(4 * radius), width=width,
            border=0, highlightthickness=0
        )
        offset = 2.5 * radius
        xpos = int((width / 2) - (5 * offset))
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
        # this code block determines if the shift lights should flash
        self.flash_display = False  # default is to not flash the display
        for trigger in reversed(shared_memory.settings.shift_triggers):
            if shared_memory.eng_rpm >= trigger['rpm']:
                self.flash_display = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

        for i, light in enumerate(self.led):
            self.my_canvas.itemconfigure(light, fill=self.led_color(i, shared_memory.eng_rpm))

    def update_gear_gauge(self):
        if shared_memory.pre_calc_gear == 0:
            displayed_gear = 'N'
        else:
            displayed_gear = str(shared_memory.pre_calc_gear)
        self.sv_gear.set(displayed_gear)

        if self.flash_display:
            if self.visible:
                self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))
            else:
                self.gear_value.configure(fg=shared_memory.settings.get_bg_color())
        else:
            self.gear_value.configure(fg=self.gear_color(rpm=shared_memory.eng_rpm))

    def process_updates(self):
        if self.main_window.get_display_mode() == DM_GEAR_SHIFT_INDICATOR:
            microsec_message(4, "Gear shift display update start")
            self.update_shift_lights()
            self.update_gear_gauge()
            self.update_rpm_gauge()
            if shared_memory.clutch_depressed:
                self.sv_clutch.set("Clutch")
            else:
                self.sv_clutch.set(" ")
            microsec_message(4, "Gear shift display update end")

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(50, self.process_updates)
        else:
            self.main_window.shutdown()

    def get_content_frame(self, width) -> tk.Frame:
        content = tk.Frame(self, width=width)
        content.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)  # for LEDs
        content.rowconfigure(1, weight=1)  # for gear number

        # widgets
        shift_lights = self.populate_shift_leds(container=content)
        shift_lights.grid(row=0, column=0)

        self.gear_value = tk.Label(
            content, textvariable=self.sv_gear,
            fg=self.gear_color(shared_memory.eng_rpm), bg=shared_memory.settings.get_bg_color(), font=self.font_gear
        )
        self.gear_value.grid(row=1, column=0)

        return content

    def get_footer_frame(self, parent: tk.Frame) -> tkinter.Frame:
        footer = build_footer(parent)

        self.sv_rpm.set(str(shared_memory.eng_rpm))
        rpm_label = tk.Label(
            footer, textvariable=self.sv_rpm, fg="white",
            bg=shared_memory.settings.get_bg_color(), font=self.font_title
        )
        rpm_label.grid(row=0, column=0, sticky='sw', padx=5, pady=5)

        clutch_label = tk.Label(
            footer, textvariable=self.sv_clutch, fg="white",
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        clutch_label.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        next_button = tk.Button(footer, text='Next', command=self.main_window.next_window)
        next_button.grid(row=0, column=2, sticky='se', padx=10, pady=10)
        return footer

    def flasher(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True
        self.after(250, self.flasher)

    def render_screen(self, parent: tk.Frame):
        format_outer_frame(self, parent.winfo_reqheight())

        header = get_header_frame(self, shared_memory.settings.get_page_title(DM_GEAR_SHIFT_INDICATOR), parent.winfo_reqwidth())
        body = self.get_content_frame(parent.winfo_reqheight())
        footer = self.get_footer_frame(self)

        header.grid(row=0, column=0, sticky='ew')
        body.grid(row=1, column=0, sticky='ew')
        footer.grid(row=2, column=0, sticky='ew')

        self.flasher()

        # pack this frame with the content above
        self.pack()


class GuiPitSpeed(tk.Frame):
    main_window = None
    my_canvas = None
    flash_display = False
    visible = True

    # this will be a StringVar that we will use as a textvariable in a Label object
    sv_speed = None

    speed_value = None
    speed_color = shared_memory.settings.default_speed_color

    font_title = None
    font_gear = None

    speed_blocks = None
    blk = []

    def __init__(self, this_window: MainWindow, parent: tk.Frame):
        super().__init__(parent)
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.main_window = this_window

        self.sv_speed = tk.StringVar()

        self.font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 4), weight='normal'
        )
        self.font_gear = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*1.1), weight='normal'
        )

        self.render_screen(parent)
        self.process_updates()

    def create_gauge(self, container: Union[tk.Tk, tk.Frame]) -> tk.Canvas:
        radius = shared_memory.settings.led_radius
        width = container.winfo_reqwidth()
        self.my_canvas = tk.Canvas(
            container, bg=shared_memory.settings.get_bg_color(),
            height=(4 * radius), width=width,
            border=0, highlightthickness=0
        )

        blk_width = 80
        blk_height = 20
        xstart = (width / 2) - (2.5 * blk_width)
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

    def flasher(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True
        self.after(250, self.flasher)

    def update_speed_gauge(self):
        self.sv_speed.set(str(shared_memory.speed))
        if self.flash_display:
            if self.visible:
                self.speed_value.configure(fg=self.speed_color)
            else:
                self.speed_value.configure(fg=shared_memory.settings.get_bg_color())
        else:
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
        self.flash_display = False  # default is to not flash the display
        for trigger in reversed(shared_memory.settings.pit_triggers):
            if shared_memory.speed >= trigger['speed']:
                self.flash_display = trigger['flash']
                # now we've done that we don't want to look for further shift_triggers matches
                break

    def process_updates(self):
        # we only want to mess with the display if it is top of the stack
        if self.main_window.get_display_mode() == DM_PIT_SPEED_INDICATOR:
            microsec_message(4, "Pit speed display update start")
            # self.sim_speed()
            self.update_speed_blocks()
            self.update_speed_gauge()
            microsec_message(4, "Pit speed display update end")
        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(50, self.process_updates)
        else:
            self.main_window.shutdown()

    def get_content_frame(self, width) -> tk.Frame:
        content = tk.Frame(self, width=width)
        content.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)  # for speed blocks
        content.rowconfigure(1, weight=1)  # for speed

        # widgets
        speed_blocks = self.create_gauge(container=content)

        self.speed_value = tk.Label(
            content, textvariable=self.sv_speed,
            fg=self.speed_color, bg=shared_memory.settings.get_bg_color(), font=self.font_gear
        )
        speed_blocks.grid(row=1, column=0)
        self.speed_value.grid(row=2, column=0)
        return content

    def get_footer_frame(self, parent: tk.Frame) -> tk.Frame:
        footer = build_footer(parent)

        pad_label = tk.Label(
            footer, text=' ', fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_title
        )
        pad_label.grid(row=0, column=0, sticky='sw', padx=5, pady=5)

        next_button = tk.Button(footer, text='Next', command=self.main_window.next_window)
        next_button.grid(row=0, column=2, sticky='se', padx=10, pady=10)
        return footer

    def render_screen(self, parent: tk.Frame):
        format_outer_frame(self, parent.winfo_reqheight())
        header = get_header_frame(self, shared_memory.settings.get_page_title(DM_PIT_SPEED_INDICATOR), parent.winfo_reqwidth())
        body = self.get_content_frame(parent.winfo_reqwidth())
        footer = self.get_footer_frame(self)

        header.grid(row=0, column=0, sticky='ew')
        body.grid(row=1, column=0, sticky='ew')
        footer.grid(row=2, column=0, sticky='ew')

        self.flasher()

        # pack this frame with the content above
        self.pack()


class BrakeTone(Sound):
    active = True
    duration = 50

    def __init__(self, frequency=0, volume=0.5):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def __call__(self):
        if self.active:
            self.play(self.duration)
        return self

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < (period / 2):
                samples[time] = +amplitude
            else:
                samples[time] = -amplitude
        return samples


class GuiBrakeTrace(tk.Frame):
    main_window = None
    my_canvas = None

    # default values at start
    x = [i for i in range(0, shared_memory.settings.get_plot_count())]
    y_brake = [0] * shared_memory.settings.get_plot_count()
    y_pedal = [0] * shared_memory.settings.get_plot_count()

    fig = None
    ax = None  # axes object for the plot
    brake_line = None  # plot line
    pedal_line = None
    ani = None
    tone_triggers = None
    last_trigger = 0

    font_title = None

    def __init__(self, this_window: MainWindow, parent: tk.Frame):
        super().__init__(parent)
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.main_window = this_window

        self.sv_speed = tk.StringVar()

        self.font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 4), weight='normal'
        )
        self.font_gear = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*1.1), weight='normal'
        )

        # generate a brake tone if necessary
        if shared_memory.settings.get_brake_tone_volume() > 0:
            pre_init(44100, -16, 1, 1024)
            pygame.init()
            self.generate_tone()

        self.render_screen(parent)

    def generate_tone(self) -> None:

        if shared_memory.brake_pressure > 0:
            quantize = 10
            freq = (quantize * int((shared_memory.brake_pressure * 6) / quantize)) + 300
            BrakeTone(frequency=freq, volume=shared_memory.settings.get_brake_tone_volume()/10)()

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(100, self.generate_tone)

    @staticmethod
    def is_flashing() -> bool:
        # the brake trace never flashes
        # we need this function as the MainWindow class calls this for every display in the list
        return False

    def build_plot(self, container, width):
        # calculate the desired width of the figure, which is full width less 80 pixels each end
        # we then need to convert the desired number of pixels into inches at a rate of 100 dpi
        # i.e. 100 pixels per inch
        width_pixels = width
        desired_pixels = width_pixels - 48
        desired_inches = desired_pixels / 100

        self.fig = plt.Figure()
        self.fig.set_figwidth(desired_inches)
        self.fig.patch.set_facecolor(shared_memory.settings.get_bg_color())

        canvas = FigureCanvasTkAgg(self.fig, master=container)
        canvas.get_tk_widget().pack()

        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.01, right=0.94)
        self.ax.set_xticks([])
        self.ax.yaxis.tick_right()
        self.ax.tick_params(axis='y', colors=shared_memory.settings.get_default_font_color())
        self.ax.set_ylim(ymax=140)

        # add the brake pressure plot
        self.brake_line, = self.ax.plot([], [])
        self.brake_line.set_color('#ff0000')

        # add the pedal position plot
        self.pedal_line, = self.ax.plot([], [])
        self.pedal_line.set_color('#00bb00')

    def animate(self, i):
        # need to check for shutdown
        if shared_memory.get_run_state() != RUN_STATE_RUNNING:
            self.main_window.shutdown()
            return

        # we only want to mess with the display if it is top of the stack
        if self.main_window.get_display_mode() == DM_BRAKE_TRACE_PLOT:

            microsec_message(4, "Brake Trace plot update start")

            # update brake pressure
            # the brake pressure multiplier is used to stretch the scale of the plot on the y-axis
            self.y_brake.pop(0)
            self.y_brake.append(shared_memory.brake_pressure * shared_memory.settings.get_pressure_multiplier())

            # update pedal position
            self.y_pedal.pop(0)
            self.y_pedal.append(shared_memory.pedal_position)  # throttle pedal position

            n = shared_memory.settings.get_plot_count()
            x = self.x[0:n]
            brake_y = self.y_brake[0:n]
            pedal_y = self.y_pedal[0:n]

            # add the brake pressure line to the graph
            self.brake_line.set_xdata(x)
            self.brake_line.set_ydata(brake_y)

            # add the pedal position line to the graph
            self.pedal_line.set_xdata(x)
            self.pedal_line.set_ydata(pedal_y)

            # set the range of the x-axis
            self.ax.set_xlim(min(x), max(x))

            # canvas.draw()
            microsec_message(4, "Brake Trace plot update end")

        return self.pedal_line,

    def get_content_frame(self) -> tk.Frame:
        content = tk.Frame(self)
        content.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.build_plot(content, self.master.winfo_reqwidth())
        return content

    def get_footer_frame(self, parent: tk.Frame) -> tk.Frame:
        footer = build_footer(parent)

        pad_label = tk.Label(
            footer, text=' ', fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_title
        )
        pad_label.grid(row=0, column=0, sticky='sw', padx=5, pady=5)

        next_button = tk.Button(footer, text='Next', command=self.main_window.next_window)
        next_button.grid(row=0, column=2, sticky='se', padx=10, pady=10)
        return footer

    def render_screen(self, parent: tk.Frame):
        format_outer_frame(self, parent.winfo_reqheight())

        header = get_header_frame(self, shared_memory.settings.get_page_title(DM_BRAKE_TRACE_PLOT), parent.winfo_reqwidth())
        body = self.get_content_frame()
        footer = self.get_footer_frame(self)

        header.grid(row=0, column=0, sticky='ew')
        body.grid(row=1, column=0, sticky='ew')
        footer.grid(row=2, column=0, sticky='ew')

        # pack this frame with the content above
        self.pack()

        self.ani = animation.FuncAnimation(
            self.fig, self.animate, shared_memory.settings.get_plot_count(), interval=50, blit=False
        )


class GuiFuelBurn(tk.Frame):
    main_window = None
    my_canvas = None
    flash_display = False
    visible = True

    sv_time_remaining = None
    sv_fuel_level = None
    sv_projected_remaining_fuel = None

    gear_value = None

    font_title = None
    font_gear = None

    screen_title = None
    shift_lights = None
    led = []
    rpm_label = None
    next_button = None

    def __init__(self, this_window: MainWindow, parent: tk.Frame):
        super().__init__(parent)
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.main_window = this_window

        self.sv_time_remaining = tk.StringVar()
        self.sv_fuel_level = tk.StringVar()
        self.sv_projected_remaining_fuel = tk.StringVar()

        self.font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 4), weight='normal'
        )
        self.font_subtitle = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size() / 6), weight='normal'
        )
        self.font_gauge = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*1.0), weight='normal'
        )
        self.font_units = font.Font(
            family='Ariel', size=int(int(shared_memory.settings.get_base_font_size())*0.4), weight='normal'
        )
        self.font_inputs = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()*0.12), weight='normal'
        )

        self.render_screen(parent)
        self.process_updates()

    def update_time_remaining(self):
        if shared_memory.race_start_time > 0:
            elapsed_secs = time.time() - shared_memory.race_start_time
            remaining_secs = (shared_memory.settings.get_race_duration() * 60) - elapsed_secs
            self.sv_time_remaining.set(convert_sss_to_mm_ss(remaining_secs))
        else:
            self.sv_time_remaining.set("--:--")

    def update_fuel_gauge(self):
        self.sv_fuel_level.set(shared_memory.current_fuel_level)

    def update_projected_remaining_fuel(self):
        if shared_memory.race_start_time > 0:
            elapsed_mins = (int(time.time()) - shared_memory.race_start_time) / 60
            fuel_used = shared_memory.starting_fuel_level - shared_memory.current_fuel_level

            # it's only after burning 2 litres can we make a reasonable calculation
            if fuel_used < 2:
                shared_memory.fuel_burn_rate = shared_memory.settings.get_default_consumption_lpm()
            else:
                shared_memory.fuel_burn_rate = fuel_used / elapsed_mins

            remaining_time = shared_memory.settings.get_race_duration() - elapsed_mins
            fuel_to_be_used = shared_memory.fuel_burn_rate * remaining_time

            # we only want to update the displayed projected number when the fuel level reduces
            # if we don't do this we get a continuously improving number as we complete more race time
            # without any change in fuel level
            if shared_memory.current_fuel_level < shared_memory.previous_fuel_level:
                self.sv_projected_remaining_fuel.set(int(round(shared_memory.current_fuel_level - fuel_to_be_used, 0)))
                shared_memory.previous_fuel_level = shared_memory.current_fuel_level
        else:
            self.sv_projected_remaining_fuel.set("---")

        return

    def process_updates(self):
        if self.main_window.get_display_mode() == DM_FUEL_BURN:
            microsec_message(4, "Fuel display update start")
            self.update_time_remaining()
            self.update_fuel_gauge()
            self.update_projected_remaining_fuel()
            microsec_message(4, "Fuel display update end")

        if shared_memory.get_run_state() == RUN_STATE_RUNNING:
            self.after(50, self.process_updates)
        else:
            self.main_window.shutdown()

    def get_content_frame(self, width) -> tk.Frame:
        content = tk.Frame(self, width=width)
        content.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=1)
        content.columnconfigure(3, weight=1)
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)
        content.rowconfigure(3, weight=1)

        # widgets
        self.time_remaining_label = tk.Label(
            content, text="Time Remaining",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_subtitle
        )

        self.time_remaining = tk.Label(
            content, textvariable=self.sv_time_remaining,
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_gauge
        )

        self.fuel_level_label = tk.Label(
            content, text="Fuel Level",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_subtitle
        )

        self.fuel_level = tk.Label(
            content, textvariable=self.sv_fuel_level,
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_gauge
        )

        self.fuel_units1 = tk.Label(
            content, text="L",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_units
        )

        self.projected_remaining_fuel_label = tk.Label(
            content, text="Projected Level",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_subtitle
        )

        self.projected_remaining_fuel = tk.Label(
            content, textvariable=self.sv_projected_remaining_fuel,
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_gauge
        )

        self.fuel_units2 = tk.Label(
            content, text="L",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_units
        )

        self.time_remaining_label.grid(row=0, column=0, columnspan=4, sticky=tk.EW)
        self.time_remaining.grid(row=1, column=0, columnspan=4, sticky=tk.EW)
        self.fuel_level_label.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        self.projected_remaining_fuel_label.grid(row=2, column=2, columnspan=2, sticky=tk.EW)
        self.fuel_level.grid(row=3, column=0, sticky=tk.SE)
        self.fuel_units1.grid(row=3, column=1, sticky=tk.SW)
        self.projected_remaining_fuel.grid(row=3, column=2, sticky=tk.SE)
        self.fuel_units2.grid(row=3, column=3, sticky=tk.SW)

        return content

    def get_footer_frame(self, parent: tk.Frame) -> tkinter.Frame:
        footer = build_footer(parent)
        next_button = tk.Button(footer, text='Next', command=self.main_window.next_window)
        next_button.grid(row=0, column=2, sticky='se', padx=10, pady=10)
        return footer

    def flasher(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True
        self.after(250, self.flasher)

    def render_screen(self, parent: tk.Frame):
        format_outer_frame(self, parent.winfo_reqheight())

        header = get_header_frame(self, shared_memory.settings.get_page_title(DM_FUEL_BURN), parent.winfo_reqwidth())
        body = self.get_content_frame(parent.winfo_reqheight())
        footer = self.get_footer_frame(self)

        header.grid(row=0, column=0, sticky='ew')
        body.grid(row=1, column=0, sticky='ew')
        footer.grid(row=2, column=0, sticky='ew')

        self.flasher()

        # pack this frame with the content above
        self.pack()


class GuiConfig(tk.Frame):
    main_window = None
    flash_display = False

    pit_speed = None  # StringVar
    speed_correction_factor = None  # StringVar
    brake_tone_volume = None  # StringVar
    fs_status = None  # IntVar

    font_title = None
    font_inputs = None

    speed_blocks = None
    blk = []

    def __init__(self, this_window: MainWindow, parent: tk.Frame):
        super().__init__(parent)
        self.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        self.main_window = this_window
        self.pit_speed = tk.StringVar()

        self.font_title = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()/4), weight='normal'
        )
        self.font_inputs = font.Font(
            family='Ariel', size=int(shared_memory.settings.get_base_font_size()*0.12), weight='normal'
        )

        self.race_duration = tk.StringVar()
        self.race_duration.set(str(shared_memory.settings.get_race_duration()))
        self.default_consumption_lpm = tk.StringVar()
        self.default_consumption_lpm.set(str(shared_memory.settings.get_default_consumption_lpm()))
        self.pit_speed = tk.StringVar()
        self.pit_speed.set(str(shared_memory.settings.get_pit_speed_limit()))
        self.speed_correction_factor = tk.StringVar()
        self.speed_correction_factor.set(str(shared_memory.settings.get_speed_correction_factor()))
        self.brake_tone_volume = tk.StringVar()
        self.brake_tone_volume.set(str(shared_memory.settings.get_brake_tone_volume()))
        self.fs_status = tk.IntVar()
        self.fs_status.set(shared_memory.settings.get_fullscreen_state())
        self.render_screen(parent)

    def update_config(self) -> None:
        shared_memory.settings.set_race_duration(self.race_duration.get())
        shared_memory.settings.set_default_consumption_lpm(self.default_consumption_lpm.get())
        shared_memory.settings.set_pit_speed_limit(self.pit_speed.get())
        shared_memory.settings.set_speed_correction_factor(self.speed_correction_factor.get())
        shared_memory.settings.set_brake_tone_volume(self.brake_tone_volume.get())
        pass

    def next_display(self) -> None:
        self.update_config()
        self.main_window.next_window()

    def is_flashing(self) -> bool:
        return self.flash_display

    def quit_yesican(self):
        self.update_config()
        shared_memory.set_run_state(RUN_STATE_PENDING_SHUTDOWN)
        self.main_window.shutdown()

    def get_content_frame(self, width: int) -> tk.Frame:
        content = tk.Frame(self)
        content.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        content.columnconfigure(0, weight=1, minsize=int(width*0.5))
        content.columnconfigure(1, weight=1, minsize=int(width*0.5))
        content.rowconfigure(0, weight=1)
        content.rowconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)
        content.rowconfigure(3, weight=1)
        content.rowconfigure(4, weight=1)
        content.rowconfigure(5, weight=1)

        race_duration = tk.Label(
            content, text="Race Duration (mins):",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        race_duration_box = tk.Entry(content, textvariable=self.race_duration)

        default_consumption_lpm = tk.Label(
            content, text="Default Fuel Burn Rate (lpm):",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        default_consumption_lpm_box = tk.Entry(content, textvariable=self.default_consumption_lpm)

        speed_limit = tk.Label(
            content, text="Pit Lane Speed Limit (kph):",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        speed_box = tk.Entry(content, textvariable=self.pit_speed)

        correction_factor_label = tk.Label(
            content, text="Speed Correction Factor:",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        correction_factor = tk.Entry(content, textvariable=self.speed_correction_factor)

        brake_tone = tk.Label(
            content, text="Brake tone volume (0 to 10):",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        volume_box = tk.Entry(content, textvariable=self.brake_tone_volume)

        fullscreen = tk.Label(
            content, text="Fullscreen Mode:",
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        fullscreen_check_box = tk.Checkbutton(
            content, variable=self.fs_status, bg=shared_memory.settings.get_bg_color(),
            borderwidth=0,
            command=lambda: shared_memory.settings.set_fullscreen_state(self.fs_status.get())
        )
        content_row = 0
        race_duration.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        race_duration_box.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        content_row += 1
        default_consumption_lpm.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        default_consumption_lpm_box.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        content_row += 1
        speed_limit.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        speed_box.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        content_row += 1
        correction_factor_label.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        correction_factor.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        content_row += 1
        brake_tone.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        volume_box.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        content_row += 1
        fullscreen.grid(row=content_row, column=0, sticky='e', padx=10, pady=5)
        fullscreen_check_box.grid(row=content_row, column=1, sticky='w', padx=10, pady=5)

        return content

    def get_footer_frame(self, parent: tk.Frame) -> tk.Frame:
        footer = build_footer(parent)

        quit_button = tk.Button(footer, text='Quit', command=self.quit_yesican)
        version = tk.Label(
            footer, text="v " + __version__,
            fg=shared_memory.settings.get_default_font_color(),
            bg=shared_memory.settings.get_bg_color(), font=self.font_inputs
        )
        next_button = tk.Button(footer, text='Next', command=self.next_display)

        quit_button.grid(row=0, column=0, sticky='sw', padx=10, pady=10)
        version.grid(row=0, column=1, sticky='ew', padx=10, pady=10)
        next_button.grid(row=0, column=2, sticky='se', padx=10, pady=10)

        return footer

    def render_screen(self, parent: tk.Frame):
        format_outer_frame(self, parent.winfo_reqheight())

        header = get_header_frame(self, shared_memory.settings.get_page_title(DM_CONFIGURATION), parent.winfo_reqwidth())
        body = self.get_content_frame(parent.winfo_reqwidth())
        footer = self.get_footer_frame(self)

        header.grid(row=0, column=0, sticky='ew')
        body.grid(row=1, column=0, sticky='ew')
        footer.grid(row=2, column=0, sticky='ew')

        # pack this frame with the content above
        self.pack()
