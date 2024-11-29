import tkinter as tk
from time import sleep

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import csv


# --- functions ---  # PEP8: `lower_case_names`

class BrakeTrail:
    # default values at start
    x = []
    y = []

    fig = None
    ax = None  # axes object for the plot
    line = None  # plot line


    def build_plot(self, container):
        self.fig = plt.Figure()

        canvas = FigureCanvasTkAgg(self.fig, master=container)
        canvas.get_tk_widget().pack()

        self.ax = self.fig.add_subplot(111)
        # ax.set_xticks([])
        self.ax.yaxis.tick_right()
        self.ax.set_ylim(ymax=140)
        self.line, = self.ax.plot([], [])

    def load_test_data(self):
        file = open('test_data_tb.csv', 'r')

        if file:
            print('read file')

            reader_csv = csv.reader(file)
            for row in reader_csv:
                if row[0] == 'Time (s)':
                    continue
                self.x.append(float(row[0]))  # time offset
                # y.append(float(row[1]))
                self.y.append(float(row[16]))  # brake pressure

            if self.x:
                self.ax.set_xlim(0, 10)
            if self.y:
                self.ax.set_ylim(min(self.y), max(self.y))

    def animate(self, i):
        # print('i:', i, x[i:i + 10], y[i:i + 10])
        sleep(0.01)

        current_x = self.x[i:i + 128]
        current_y = self.y[i:i + 128]

        self.line.set_xdata(current_x)
        self.line.set_ydata(current_y)
        self.line.set_color('r')

        if current_x:
            self.ax.set_xlim(min(current_x), max(current_x))

        # canvas.draw()

        return self.line,


    # --- main ---

    def run_plot(self):
        # - GUI -

        try:
            self.ani = animation.FuncAnimation(self.fig, self.animate, 512, interval=0, blit=False)

        except NameError as ex:
            print(ex)

if __name__ == "__main__":
    bt_plot = BrakeTrail()
    tk_top = tk.Tk()
    bt_plot.build_plot(tk_top)
    bt_plot.load_test_data()
    bt_plot.run_plot()
    print('mainloop')
    tk_top.mainloop()
