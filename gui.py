import tkinter as tk
import tkinter.font as font

from _version import __version__
from settings import *


def create_circle(x, y, r, canvas, color):  # center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline=color, fill=color)


class GuiPitSpeed:

    my_root = None

    def __init__(self, window_root):
        self.my_root = window_root

    def render_screen(self):
        settings = Settings()
        
        font_title = font.Font(family='Ariel', size=(int(settings.base_font_size/4)), weight='normal')
        font_speed = font.Font(family='Ariel', size=settings.base_font_size, weight='normal')
        font_kph = font.Font(family='Ariel', size=(int(settings.base_font_size/4)), weight='normal')

        frame_top = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)
        screen_title = tk.Label(
            frame_top, text=settings.pit_screen_title,
            width=20, pady=20, fg='white', bg=settings.bg_color, font=font_title
        )
        screen_title.pack()
        frame_top.pack()

        frame_upper_middle = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)

        my_canvas = tk.Canvas(
            frame_upper_middle, bg=settings.bg_color, height=100, width=800, border=0, highlightthickness=0
        )
        xpos = 96
        offset = 60
        create_circle(xpos, 50, 20, my_canvas, settings.led_clr[0])
        create_circle(xpos+(1*offset), 50, 20, my_canvas, settings.led_clr[0])
        create_circle(xpos+(2*offset), 50, 20, my_canvas, settings.led_clr[0])
        create_circle(xpos+(3*offset), 50, 20, my_canvas, settings.led_clr[0])

        create_circle(xpos+(4*offset), 50, 20, my_canvas, settings.led_clr[1])
        create_circle(xpos+(5*offset), 50, 20, my_canvas, settings.led_clr[1])
        create_circle(xpos+(6*offset), 50, 20, my_canvas, settings.led_clr[1])
        create_circle(xpos+(7*offset), 50, 20, my_canvas, settings.led_clr[1])

        create_circle(xpos+(8*offset), 50, 20, my_canvas, settings.led_clr[2])
        create_circle(xpos+(9*offset), 50, 20, my_canvas, settings.led_clr[2])
        create_circle(xpos+(10*offset), 50, 20, my_canvas, settings.led_clr[2])

        my_canvas.pack()

        frame_upper_middle.pack()

        frame_lower_middle = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)
        speed_value = tk.Label(
            frame_lower_middle, text="49", fg='white', bg=settings.bg_color, font=font_speed, anchor=tk.S
        )
        speed_kph = tk.Label(
            frame_lower_middle, text=" kph", fg='white', bg=settings.bg_color, font=font_kph, anchor=tk.S
        )
        speed_value.grid(row=0, column=0, sticky=tk.S)
        speed_kph.grid(row=0, column=1, sticky=tk.S)
        frame_lower_middle.pack()

        frame_footer = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)
        config_button = tk.Button(frame_footer, text="Conf")
        config_button.grid(row=0, column=1)
        frame_footer.pack(anchor=tk.E, padx=5, pady=5)

        self.my_root.mainloop()


class GuiGearShift:

    my_root = None

    def __init__(self, window_root):
        self.my_root = window_root

    @staticmethod
    def populate_shift_leds(led_frame, rpm=6555):
        settings = Settings()
        radius = settings.led_radius
        my_canvas = tk.Canvas(
            led_frame, bg=settings.bg_color,
            height=(4 * radius), width=settings.screen_width,
            border=0, highlightthickness=0
        )
        offset = 2.5 * radius
        xpos = (480 / 2) - (5 * offset)
        ypos = 2 * radius
        i = 0

        for trigger in settings.shift_triggers:
            if trigger['flash']:
                continue  # we need to handle flashing screen
            if rpm >= trigger['rpm']:
                create_circle(xpos + (i * offset), ypos, radius, my_canvas, trigger['led'])
            else:
                create_circle(xpos + (i * offset), ypos, radius, my_canvas, settings.led_off_color)
            i += 1

        my_canvas.pack()

    def render_screen(self):
        eng_rpm = 6999

        settings = Settings()

        font_title = font.Font(family='Ariel', size=(int(settings.base_font_size/4)), weight='normal')
        font_speed = font.Font(family='Ariel', size=settings.base_font_size, weight='normal')
        font_footer = font.Font(family='Ariel', size=int(settings.base_font_size/8), weight='normal')

        frame_top = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)
        screen_title = tk.Label(
            frame_top, text=settings.shift_screen_title,
            width=20, pady=12, fg='white', bg=settings.bg_color, font=font_title
        )
        screen_title.pack()
        frame_top.pack()

        frame_upper_middle = tk.LabelFrame(
            self.my_root, bg=settings.bg_color, borderwidth=0, height=int(settings.screen_height/3)
        )

        self.populate_shift_leds(led_frame=frame_upper_middle, rpm=eng_rpm)

        frame_upper_middle.pack()

        frame_lower_middle = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)

        gear_text_color = settings.default_gear_color
        for trigger in settings.shift_triggers:
            if eng_rpm >= trigger['rpm']:
                gear_text_color = trigger['gear_color']

        gear_value = tk.Label(frame_lower_middle, text="3", fg=gear_text_color, bg=settings.bg_color, font=font_speed)
        gear_value.pack()
        frame_lower_middle.pack()

        frame_footer = tk.LabelFrame(self.my_root, bg=settings.bg_color, borderwidth=0)
        # version = tk.Label(frame_footer, text=__version__, fg=gear_text_color, bg=settings.bg_color, font=font_footer)
        # version.grid(row=0, column=0, sticky="nsew")
        # frame_footer.grid_columnconfigure(0, weight=1, uniform="column")
        # config_button = tk.Button(frame_footer, text="Conf")
        # config_button.grid(row=0, column=1, sticky="nsew")
        # frame_footer.grid_columnconfigure(1, weight=1, uniform="column")

        columns = []
        for i in range(6):
            frame = tk.Frame(frame_footer, borderwidth=1, relief="raised", background="bisque")
            columns.append(frame)

        frame_footer.grid_rowconfigure(0, weight=1)
        for column, f in enumerate(columns):
            f.grid(row=0, column=column, sticky="nsew")
            frame_footer.grid_columnconfigure(column, weight=1, uniform="column")

        # frame_footer.pack(padx=5, pady=5)

        self.my_root.mainloop()
