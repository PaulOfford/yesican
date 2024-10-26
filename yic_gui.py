import queue
import tkinter as tk
import tkinter.font as font
import locale
import functools as ft
import re

from _version import __version__
from settings import *
from message_q import *

root = tk.Tk()
window_title = "YesICAN Client " + __version__
root.title(window_title)
root.geometry(settings.startup_dimensions)

font_btn = font.Font(family='Ariel', size=(int(settings.font_size*1.125)), weight='normal')
font_btn_bold = font.Font(family='Ariel', size=(int(settings.font_size*1.125)), weight='bold')
font_hdr = font.Font(family='Ariel', size=(int(settings.font_size*1.75)), weight='normal')
font_freq = font.Font(family='Seven Segment', size=(int(settings.font_size*3)), weight='normal')
font_main = font.Font(family='Ariel', size=settings.font_size, weight='normal')
font_main_ul = font.Font(family='Ariel', size=settings.font_size, weight='normal', underline=True)
font_main_hdr = font.Font(family='Ariel', size=(int(settings.font_size*1.25)), weight='normal')
font_main_bold = font.Font(family='Ariel', size=settings.font_size, weight='bold')


def settings_window():
    sw = tk.Tk()
    sw.title("Settings")
    sw.geometry("400x320")

    label_list = [
        ('startup_width', 'Window Startup Width:', 'entry', tk.IntVar(sw)),
        ('startup_height', 'Window Startup Height:', 'entry', tk.IntVar(sw)),
        ('font_size', 'Font Size:', 'entry', tk.IntVar(sw)),
        ('max_latest', 'Max Latest:', 'entry', tk.IntVar(sw)),
        ('max_qsos', 'Max QSOs:', 'entry', tk.IntVar(sw)),
        ('max_blogs', 'Max Blogs:', 'entry', tk.IntVar(sw)),
        ('max_listing', 'Max Listing:', 'entry', tk.IntVar(sw)),
        ('use_gmt', 'Use GMT for Clock and Log:', 'checkbox', tk.IntVar(sw)),
    ]
    entry_list = []

    # Row and Column configure to manage weights
    sw.columnconfigure(0, weight=1)
    sw.columnconfigure(2, weight=1)
    sw.rowconfigure(0, weight=1)
    sw.rowconfigure(2, weight=1)

    # Add a frame to hold the rest of the widgets and place that frame in the row/column without a weight.
    # This will allow us to center everything that we place in the frame.
    sw_frame = tk.Frame(sw)
    sw_frame.grid(row=1, column=1)

    # create the labels and entry widgets
    for i, label in enumerate(label_list):
        tk.Label(sw_frame, text=label[1] + ' ', font='8').grid(row=i, column=0, sticky='w')
        # Store the entry widgets in a list for later use
        if label[2] == 'entry':
            entry_list.append(tk.Entry(sw_frame, borderwidth=2, width=8, font='8', relief=tk.GROOVE))
            entry_list[-1].grid(row=i, column=1)
            entry_list[-1].insert(0, settings.get_setting(label[0]))
        elif label[2] == 'checkbox':
            entry_list.append(
                tk.Checkbutton(
                    sw_frame, justify='left', onvalue=1, offvalue=0, variable=label[3]
                )
            )
            entry_list[-1].grid(row=i, column=1)
            if settings.get_setting(label[0]) == 1:
                entry_list[-1].select()
            pass

    # save the settings
    def save_entries():
        for j, entry in enumerate(entry_list):
            my_label = label_list[j]
            if entry.widgetName == 'entry':
                settings.set_setting(my_label[0], entry.get())
            elif entry.widgetName == 'checkbutton':
                print(my_label[3].get())
                if my_label[3].get():
                    db_value = 1
                else:
                    db_value = 0
                settings.set_setting(my_label[0], db_value)
        sw.destroy()

    tk.Label(sw_frame, text=' ').grid(row=len(label_list)+1, column=0, columnspan=2)
    tk.Button(
        sw_frame, text='Cancel', font='8', command=sw.destroy
    ).grid(row=len(label_list)+2, column=0)
    tk.Button(
        sw_frame, text='Save', font='8', command=save_entries
    ).grid(row=len(label_list)+2, column=1)


class GuiHeader:

    js8_freqs = [1.842, 3.578, 7.078, 10.130, 14.078, 18.104, 21.078, 24.922, 27.245, 28.078, 50.318]

    is_scanning = False
    freq_text = tk.StringVar()
    offset_text = tk.StringVar()
    callsign_text = tk.StringVar()
    scan_btn = None
    clock_label = None

    def __init__(self, header_frame):

        frame_hdr_left = tk.Frame(header_frame, bg='black')
        frame_hdr_left.pack(expand=True, fill='y', side='left')
        frame_hdr_mid = tk.Frame(header_frame, bg='black')
        frame_hdr_mid.pack(expand=True, fill='y', side='left')
        frame_hdr_right = tk.Frame(header_frame, bg='black')
        frame_hdr_right.pack(expand=True, fill='y', side='left')

        frame_cell_1 = tk.Frame(frame_hdr_left, bg='black')
        frame_cell_1.pack(expand=True, fill='both')
        # frequency in the header
        hdr_freq = tk.Label(
            frame_cell_1,
            textvariable=self.freq_text,
            bg='black', fg='white',
            font=font_freq,
            justify='center',
        )
        hdr_freq.pack()

        frame_cell_4 = tk.Frame(frame_hdr_left, bg='black')
        frame_cell_4.pack(expand=True, fill='both')
        hdr_offset = tk.Label(
            frame_cell_4,
            textvariable=self.offset_text,
            bg='black', fg='white',
            font=font_hdr,
            justify='center',
        )
        hdr_offset.pack()

        # Callsign
        frame_cell_2 = tk.Frame(frame_hdr_mid, bg='black')
        frame_cell_2.pack(expand=True, fill='both')
        hdr_callsign = tk.Label(
            frame_cell_2,
            textvariable=self.callsign_text,
            bg='black', fg='white',
            font=font_hdr
        )
        hdr_callsign.pack()

        # Clock
        frame_cell_5 = tk.Frame(frame_hdr_mid, bg='black')
        frame_cell_5.pack(expand=True, fill='both')
        self.clock_label = tk.Label(
            frame_cell_5,
            bg='black', fg='white',
            font=font_hdr,
        )
        self.clock_label.pack()

        # Scan button
        frame_cell_3 = tk.Frame(frame_hdr_right, bg='black')
        frame_cell_3.pack(expand=True, fill='both')
        self.scan_btn = tk.Button(
            frame_cell_3,
            text='Scan',
            font=font_btn_bold,
            bg='#22ff23', height=1, width=18,
            relief='flat',
            command=self.toggle_scan
        )
        self.scan_btn.pack()

        # Blank Cell
        frame_cell_6 = tk.Frame(frame_hdr_right, bg='black')
        frame_cell_6.pack(expand=True, fill='both')
        hdr_blank = tk.Label(
            frame_cell_6,
            text='',
            bg='black', fg='white',
            font=font_hdr
        )
        hdr_blank.pack()

        self.reload_header()

    def clock_tick(self, curtime=''):  # used for the header clock
        if settings.use_gmt:
            newtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
        else:
            newtime = time.strftime('%Y-%m-%d %H:%M:%S')

        if newtime != curtime:
            curtime = newtime
            self.clock_label.config(text=curtime)
        self.clock_label.after(200, self.clock_tick, curtime)

    def toggle_scan(self):
        if self.is_scanning:
            self.is_scanning = False
            self.scan_btn.configure(bg='#22ff23')
        else:
            self.is_scanning = True
            self.scan_btn.configure(bg='#ff2222')

    def set_frequency(self):
        self.freq_text.set('123456')

    def set_offset(self):
        self.offset_text.set('4567' + ' Hz')

    def set_callsign(self):
        self.callsign_text.set('M0PXO')

    def reload_header(self):
        pass



class GuiPitSpeedLimiter:

    qso_box = []

    prev_is_listing = False

    qso_cols = ['qso_date', 'type', 'blog', 'station', 'cmd', 'rsp', 'post_id', 'post_date', 'title',
                'body']

    def __init__(self, frame: tk.Frame):

        self.qso_box = tk.Text(frame, width=960, wrap=tk.WORD, padx=10, pady=10,
                               font=font_main, bg='#595959',
                               spacing1=1.1, spacing2=1.1)

        self.qso_box.pack(fill=tk.BOTH, expand=1, anchor='ne')

    def reload_qso_box(self):
        pass

class GuiMain:

    def __init__(self, frame):
        pane_main = tk.PanedWindow(frame, bg='#595959')
        pane_main.pack(fill='both', expand=1, side='top')

        # frame_left = tk.Frame(pane_main, bg='white')
        # pane_main.add(frame_left, width=300)

        frame_mid = tk.Frame(pane_main, bg='#595959')
        pane_main.add(frame_mid, width=960)

        # frame_right = tk.Frame(pane_main, bg='white')
        # pane_main.add(frame_right, width=300)
        #
        # # Latest Posts area
        # frame_latest_list = tk.Frame(frame_left, bg='white')
        # frame_latest_list.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # QSO Area follows - middle of main
        frame_qso = tk.Frame(frame_mid)
        frame_qso.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.qso_box = GuiPitSpeedLimiter(frame_qso)

        # frame_cli = tk.Frame(frame_mid)
        # frame_cli.pack(side=tk.BOTTOM, padx=4)

        # self.cli = GuiCli(frame_mid)

        # Blog list area - right of main
        # frame_blog_list = tk.Frame(frame_right, bg='white', padx=4, pady=4)
        # frame_blog_list.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # self.blog_list = GuiBlogList(frame_blog_list)

    def reload_latest(self):
        self.latest_posts.reload_latest()

    def reload_qso_box(self):
        self.qso_box.reload_qso_box()

    def reload_cli(self):
        pass

    def reload_blog_list(self):
        pass
