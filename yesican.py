from gui import *
import tkinter as tk


class GearShiftWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Gear Shift").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)


class PitSpeedWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        tk.Label(self, text="Pit Speed").pack(padx=10, pady=10)
        self.pack(padx=10, pady=10)


class MainWindow:
    def __init__(self, master):
        self.myRoot = master
        mainframe = tk.Frame(master)
        mainframe.configure(bg=settings.bg_color)
        mainframe.pack(fill='both', expand=1)
        self.index = 0

        self.frameList = [GearShiftWindow(mainframe), PitSpeedWindow(mainframe)]
        self.frameList[1].forget()

        # bottomframe = tk.Frame(master)
        # bottomframe.pack(padx=10, pady=10)
        #
        # switch = tk.Button(bottomframe, text='Switch', command=self.changeWindow)
        # switch.pack(padx=10, pady=10)

    def changeWindow(self):
        self.frameList[self.index].forget()
        self.index = (self.index + 1) % len(self.frameList)
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack(padx=10, pady=10)

    def checkSwitch(self):
        self.changeWindow()
        self.myRoot.after(1000, self.checkSwitch)

if __name__ == "__main__":
    settings = Settings()

    root = tk.Tk()
    root.geometry(str(settings.screen_width) + "x" + str(settings.screen_height))
    root.configure(bg=settings.bg_color)
    window = MainWindow(root)
    root.after(1000, window.checkSwitch)
    root.mainloop()

    # while True:
    #     gs_window = tk.Tk()
    #     gs_window.geometry(str(settings.screen_width) + "x" + str(settings.screen_height))
    #     gs_window.configure(bg=settings.bg_color)
    #
    #     sv_rpm = tk.StringVar()
    #     sv_gear = tk.StringVar()
    #
    #     shift = GuiGearShift(window_root=gs_window)
    #     shift.render_screen(sv_gear, sv_rpm)
    #     gs_window.after(200, shift.process_updates)
    #     gs_window.mainloop()
    #
    #     ps_window = tk.Tk()
    #     ps_window.geometry(str(settings.screen_width) + "x" + str(settings.screen_height))
    #     ps_window.configure(bg=settings.bg_color)
    #
    #     sv_speed = tk.StringVar()
    #
    #     pit = GuiPitSpeed(window_root=ps_window)
    #     pit.render_screen(sv_gear, sv_rpm)
    #     ps_window.after(200, shift.process_updates)
    #     ps_window.mainloop()
