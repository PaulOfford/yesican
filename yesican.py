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
from switcher import Switcher


class MainWindow:
    presentation = None
    switcher = None

    frame_list = []
    display_mode = 0
    saved_display_mode = 0
    visible = True
    pit_speed_switch = False  # True - closed, False - open

    def __init__(self, container, master):
        self.presentation = container
        mainframe = tk.Frame(master)
        mainframe.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        mainframe.pack()

        # any change to the following list must be matched with changes to the DM_ ... values on constants.py
        self.frame_list = [
            GuiGearShift(self, mainframe), GuiPitSpeed(self, mainframe),
            GuiBrakeTrace(self, mainframe), GuiConfig(self, mainframe)
        ]

        for i in range(1, len(self.frame_list)):
            self.frame_list[i].forget()
        self.blank_display = GuiBlank(mainframe)
        self.blank_display.forget()

        self.switcher = Switcher(len(self.frame_list))

    def shutdown(self) -> None:
        self.switcher.end_gpio()
        self.presentation.shutdown()

    def get_window_height(self) -> int:
        return self.presentation.get_window_height()

    def get_window_width(self) -> int:
        return self.presentation.get_window_width()

    def get_display_mode(self) -> int:
        return self.display_mode

    def change_window(self, desired_display_mode: int) -> None:
        self.frame_list[self.display_mode].forget()
        self.frame_list[desired_display_mode].tkraise()
        self.frame_list[desired_display_mode].pack()
        self.display_mode = desired_display_mode

    def next_window(self):
        self.switcher.step_display_mode()

    def check_display_mode(self, master):
        if self.switcher.get_target_display_mode() != self.display_mode:
            self.change_window(desired_display_mode=self.switcher.get_target_display_mode())

        # this doesn't have to run at a high frequency as it only processes button and switch events
        master.after(250, lambda: self.check_display_mode(master))


class Presentation:

    canbus = None
    backend_thread = None
    root = None

    def __init__(self):
        shared_memory.set_run_state(RUN_STATE_RUNNING)
        shared_memory.settings = Settings()
        shared_memory.settings.read_config()

        # start backend thread
        self.canbus = CanInterface()
        self.backend_thread = threading.Thread(target=self.canbus.read_messages)
        self.backend_thread.start()

    def get_window_height(self) -> int:
        return self.root.winfo_height()

    def get_window_width(self) -> int:
        return self.root.winfo_width()

    def shutdown(self):
        microsec_message(1, "Shutdown requested")
        shared_memory.run_state = RUN_STATE_AWAITING_BACKEND
        time.sleep(0.2)

        self.kick_backend()

        microsec_message(1, "Shutdown checking that the backend thread has exited")
        self.backend_thread.join(0.5)  # wait for up to 500ms for the backend thread to exit

        self.root.destroy()
        microsec_message(1, "Shutdown done - exiting")
        shared_memory.run_state = RUN_STATE_EXITING
        exit(0)

    def run_presentation(self):
        microsec_message(1, "Presentation started")
        self.root = tk.Tk()
        self.root.config(cursor='none')

        if shared_memory.settings.get_fullscreen_state():
            self.root.wm_attributes('-fullscreen', 'True')
        self.root.geometry(
            str(shared_memory.settings.get_screen_width()) + "x" + str(shared_memory.settings.get_screen_height())
        )
        self.root.configure(bg=shared_memory.settings.get_bg_color())
        self.root.update()  # we have to do this so that later code can get the window size

        window = MainWindow(self, self.root)
        self.root.protocol("WM_DELETE_WINDOW", window.shutdown)
        self.root.after(100, lambda: window.check_display_mode(self.root))
        self.root.mainloop()

    def kick_backend(self):
        self.canbus.kick_backend()


if __name__ == "__main__":
    microsec_message(1, "YesICan " + __version__ + " starting")

    if platform.system() != 'Linux' and platform.system() != 'Windows':
        microsec_message(1, "Unsupported platform")
        exit(0)

    presentation = Presentation()
    presentation.run_presentation()
