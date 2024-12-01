import platform
import threading
import time

import switcher

from settings_code import Settings
from gui import *
from can_interface import CanInterface
from _version import __version__
from my_logger import microsec_message
from constants import *

presentation = None


class MainWindow:
    frame_list = []
    index = 0
    visible = True
    flash = False

    def __init__(self, master):
        mainframe = tk.Frame(master)
        mainframe.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        mainframe.pack()

        self.frame_list = [GuiGearShift(self, mainframe), GuiPitSpeed(self, mainframe), GuiConfig(self, mainframe)]

        for i in range(1, len(self.frame_list)):
            self.frame_list[i].forget()
        self.blank_display = GuiBlank(mainframe)
        self.blank_display.forget()

    def change_window(self, display_mode):
        self.frame_list[self.index].forget()
        self.frame_list[display_mode].tkraise()
        self.frame_list[display_mode].pack()
        self.index = display_mode
        self.flash = False
        self.visible = True

        shared_memory.current_mode = shared_memory.desired_mode

    def next_window(self):
        next_mode = (self.index + 1) % len(self.frame_list)
        microsec_message(2, "Next button to mode " + str(next_mode))
        self.change_window(next_mode)

    def flash_window(self) -> None:
        if self.visible and self.frame_list[shared_memory.current_mode].is_flashing():
            self.frame_list[self.index].forget()
            self.blank_display.tkraise()  # assumes blank is last frame in the frame_list
            self.visible = False
            self.blank_display.pack()
        else:
            self.blank_display.forget()  # assumes blank is last frame in the frame_list
            self.frame_list[self.index].tkraise()
            self.visible = True
            self.frame_list[self.index].pack()

    def check_switch(self, master):
        # check the physical pit speed limiter switch
        if switcher.is_switch_on():
            if not shared_memory.pit_speed_switch:
                microsec_message(1, "Switch to Pit Speed display")
                shared_memory.desired_mode = 1
                self.change_window(shared_memory.desired_mode)
                shared_memory.pit_speed_switch = True
        else:
            if shared_memory.pit_speed_switch:
                microsec_message(1, "Switch to Gear Shift display")
                shared_memory.desired_mode = 0
                self.change_window(shared_memory.desired_mode)
                shared_memory.pit_speed_switch = False

        if shared_memory.current_mode != shared_memory.desired_mode:
            self.next_window()

        # this doesn't have to run at a high frequency as it only processes button and switch events
        master.after(250, lambda: self.check_switch(master))

    @staticmethod
    def yesican_shutdown():
        microsec_message(1, "Shutdown requested")
        shared_memory.run_state = RUN_STATE_AWAITING_BACKEND
        time.sleep(0.2)
    
        presentation.kick_backend()
    
        microsec_message(1, "Shutdown checking that the backend thread has exited")
        shared_memory.backend_thread.join(0.5)  # wait for up to 500ms for the backend thread to exit
    
        shared_memory.root.destroy()
        microsec_message(1, "Shutdown done - exiting")
        shared_memory.run_state = RUN_STATE_EXITING
        exit(0)


class Presentation:

    canbus = None

    def __init__(self):
        shared_memory.settings = Settings()
        shared_memory.settings.read_config()

        # start backend thread
        self.canbus = CanInterface()
        shared_memory.backend_thread = threading.Thread(target=self.canbus.read_messages)
        shared_memory.backend_thread.start()

    @staticmethod
    def run_presentation():
        microsec_message(1, "Presentation started")
        shared_memory.root = tk.Tk()
        shared_memory.root.config(cursor='none')

        if shared_memory.settings.get_fullscreen_state():
            shared_memory.root.wm_attributes('-fullscreen', 'True')
        shared_memory.root.geometry(
            str(shared_memory.settings.get_screen_width()) + "x" + str(shared_memory.settings.get_screen_height())
        )
        shared_memory.root.configure(bg=shared_memory.settings.get_bg_color())
        shared_memory.root.update()  # we have to do this so that later code can get the window size

        window = MainWindow(shared_memory.root)
        shared_memory.root.protocol("WM_DELETE_WINDOW", window.yesican_shutdown)
        shared_memory.root.after(100, lambda: window.check_switch(shared_memory.root))
        shared_memory.root.mainloop()

    def kick_backend(self):
        self.canbus.kick_backend()


if __name__ == "__main__":
    microsec_message(1, "YesICan " + __version__ + " starting")

    if platform.system() != 'Linux' and platform.system() != 'Windows':
        microsec_message(1, "Unsupported platform")
        exit(0)

    presentation = Presentation()
    presentation.run_presentation()
