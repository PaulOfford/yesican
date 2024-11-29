import tkinter as tk
from time import sleep
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

import csv

import random


# --- functions ---  # PEP8: `lower_case_names`

def open_file():
    global x
    global y

    # file = filedialog.askopenfile(filetypes=[('CSV Files', '*.csv'),
    #                                          ('Text Files', '*.txt'),
    #                                          ('All Files', '*.*')])

    file = open('test_data_tb.csv', 'r')

    if file:
        print('read file')

        x = []
        y = []

        reader_csv = csv.reader(file)
        for row in reader_csv:
            if row[0] == 'Time (s)':
                continue
            x.append(float(row[0]))  # time offset
            # y.append(float(row[1]))
            y.append(float(row[16]))  # brake pressure

        if x:
            ax.set_xlim(0, 10)
        if y:
            ax.set_ylim(min(y), max(y))


def animate(i):
    # print('i:', i, x[i:i + 10], y[i:i + 10])
    sleep(0.05)

    current_x = x[i:i + 128]
    current_y = y[i:i + 128]

    line.set_xdata(current_x)
    line.set_ydata(current_y)
    line.set_color('r')

    if current_x:
        ax.set_xlim(min(current_x), max(current_x))

    # canvas.draw()

    return line,


# --- main ---

# default values at start
x = []
y = []

# - GUI -

tk_top = tk.Tk()

try:
    fig = plt.Figure()

    canvas = FigureCanvasTkAgg(fig, master=tk_top)
    canvas.get_tk_widget().pack()

    ax = fig.add_subplot(111)
    open_file()
    # ax.set_xticks([])
    ax.set_ylim(ymax=140)
    line, = ax.plot([], [])

    # ani = animation.FuncAnimation(fig, animate, 250, interval=250, blit=False)
    ani = animation.FuncAnimation(fig, animate, 512, interval=0, blit=False)
    # ani = animation.FuncAnimation(fig, animate, 512, blit=False)

except NameError as ex:
    print(ex)

print('mainloop')
tk_top.mainloop()