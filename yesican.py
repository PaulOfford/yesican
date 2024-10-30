from gui import *
import tkinter as tk
import shared_memory


class MainWindow:

    index = 0
    visible = True

    def __init__(self, master):
        mainframe = tk.Frame(master)
        mainframe.configure(bg=settings.bg_color, borderwidth=0)
        mainframe.pack()

        self.frameList = [GuiGearShift(mainframe), GuiPitSpeed(mainframe), GuiConfig(mainframe)]
        shared_memory.no_of_modes = len(self.frameList)
        for i in range(1,shared_memory.no_of_modes):
            self.frameList[i].forget()
        self.blank_display = GuiBlank(mainframe)
        self.blank_display.forget()

    def change_window(self):
        self.frameList[self.index].forget()
        self.index = (self.index + 1) % len(self.frameList)
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack()

        shared_memory.current_mode = shared_memory.desired_mode

    def flash_window(self) -> None:
        if shared_memory.eng_rpm >= 7000:
            stop = True
        if shared_memory.flash_window:
            if self.visible:
                self.frameList[self.index].forget()
                self.blank_display.tkraise()  # assumes blank is last frame in the framelist
                self.visible = False
                self.blank_display.pack()
            else:
                self.blank_display.forget()  # assumes blank is last frame in the framelist
                self.frameList[self.index].tkraise()
                self.visible = True
                self.frameList[self.index].pack()
        else:
            self.visible = True
            self.blank_display.forget()
            self.frameList[self.index].tkraise()
            self.frameList[self.index].pack()

    def check_switch(self, master):
        self.flash_window()
        if shared_memory.current_mode != shared_memory.desired_mode:
            self.change_window()
        master.after(250, lambda: self.check_switch(master))


if __name__ == "__main__":
    settings = Settings()

    root = tk.Tk()
    # root.overrideredirect(True)
    # root.wm_attributes('-fullscreen', 'True')
    root.geometry(str(settings.screen_width) + "x" + str(settings.screen_height))
    root.configure(bg=settings.bg_color)
    window = MainWindow(root)
    root.after(100, lambda: window.check_switch(root))
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
