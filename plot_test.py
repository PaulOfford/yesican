import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import csv


# --- functions ---  # PEP8: `lower_case_names`

class BrakeTrail:
    # default values at start
    x_axis = []
    y_brake = []
    y_pedal = []

    fig = None
    ax = None
    brake_line = None  # plot line
    pedal_line = None  # plot line
    ani = None

    def build_plot(self, container):
        self.fig = plt.Figure()

        canvas = FigureCanvasTkAgg(self.fig, master=container)
        canvas.get_tk_widget().pack()

        self.ax = self.fig.add_subplot(111)
        self.ax.set_xticks([])
        self.ax.yaxis.tick_right()
        self.ax.set_ylim(0, 120)

        # add the brake pressure plot
        self.brake_line, = self.ax.plot([], [])
        self.brake_line.set_color('#ff0000')

        # add the pedal position plot
        self.pedal_line, = self.ax.plot([], [])
        self.pedal_line.set_color('#00bb00')

    def load_test_data(self):
        file = open('test_data.csv', 'r')

        if file:
            print('read file')

            reader_csv = csv.reader(file)
            for row in reader_csv:
                if row[0] == 'Time (s)':
                    continue
                self.x_axis.append(float(row[0]))  # time offset
                self.y_brake.append(float(row[16]))  # brake pressure
                self.y_pedal.append(float(row[17]))  # pedal position

    def animate(self, i):
        x = self.x_axis[i:i + 128]
        brake_y = self.y_brake[i:i + 128]
        pedal_y = self.y_pedal[i:i + 128]

        self.brake_line.set_xdata(x)
        self.brake_line.set_ydata(brake_y)

        self.pedal_line.set_xdata(x)
        self.pedal_line.set_ydata(pedal_y)

        if x:
            self.ax.set_xlim(min(x), max(x))

        return self.pedal_line,

    def run_plot(self):
        # animate with a frame rate of 20 fps (or every 50 ms) to match data rate
        self.ani = animation.FuncAnimation(self.fig, self.animate, 512, interval=50, blit=False)

if __name__ == "__main__":
    bt_plot = BrakeTrail()
    tk_top = tk.Tk()
    bt_plot.build_plot(tk_top)
    bt_plot.load_test_data()
    bt_plot.run_plot()
    print('mainloop')
    tk_top.mainloop()
