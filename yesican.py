import platform
import threading
import time
import tkinter as tk
import can

import switcher
import shared_memory

from settings_code import Settings
from gui import *
from can_interface import CanInterface
from _version import __version__
from my_logger import microsec_message
from constants import *


def yesican_shutdown():
    microsec_message(1, "Shutdown requested")
    shared_memory.run_state = RUN_STATE_AWAITING_BACKEND
    time.sleep(0.2)

    if shared_memory.bus_vector:
        microsec_message(1, "Give the backend a kick to trigger thread exit")
        # give the can interface a kick in case we don't have incoming messages
        msg = can.Message(arbitration_id=0x2fa, data=[0xff, 0xff, 0xff, 0xff, 0xff], is_extended_id=False)
        try:
            # this may not work if can interface is already shut
            shared_memory.bus_vector.send(msg)
        except:
            pass

    microsec_message(1, "Shutdown checking that the backend thread has exited")
    shared_memory.backend_thread.join(0.5)  # wait for up to 500ms for the backend thread to exit

    shared_memory.root.destroy()
    microsec_message(1, "Shutdown done - exiting")
    shared_memory.run_state = RUN_STATE_EXITING
    exit(0)


class MainWindow:

    index = 0
    visible = True

    def __init__(self, master):
        mainframe = tk.Frame(master)
        mainframe.configure(bg=shared_memory.settings.get_bg_color(), borderwidth=0)
        mainframe.pack()

        self.frameList = [GuiGearShift(mainframe), GuiPitSpeed(mainframe), GuiConfig(mainframe)]
        shared_memory.no_of_modes = len(self.frameList)
        for i in range(1, shared_memory.no_of_modes):
            self.frameList[i].forget()
        self.blank_display = GuiBlank(mainframe)
        self.blank_display.forget()

    def change_window(self, display_mode):
        self.frameList[self.index].forget()
        self.frameList[display_mode].tkraise()
        self.frameList[display_mode].pack()
        self.index = display_mode
        self.visible = True

        shared_memory.current_mode = shared_memory.desired_mode

    def next_window(self):
        next_mode = (self.index + 1) % len(self.frameList)
        microsec_message(2, "Next button to mode " + str(next_mode))
        self.change_window(next_mode)

    def flash_window(self, flash: bool) -> None:
        if self.visible and flash:
            self.frameList[self.index].forget()
            self.blank_display.tkraise()  # assumes blank is last frame in the framelist
            self.visible = False
            self.blank_display.pack()
        else:
            self.blank_display.forget()  # assumes blank is last frame in the framelist
            self.frameList[self.index].tkraise()
            self.visible = True
            self.frameList[self.index].pack()

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
        if shared_memory.flash_window and shared_memory.current_mode < len(self.frameList) - 1:
            self.flash_window(flash=True)
        elif not self.visible:
            self.flash_window(flash=False)
        # this doesn't have to run at a high frequency as it only processes button and switch events
        master.after(250, lambda: self.check_switch(master))


class Presentation:

    def __init__(self):
        shared_memory.settings = Settings()
        shared_memory.settings.read_config()

        # start backend thread
        canbus = CanInterface()
        shared_memory.backend_thread = threading.Thread(target=canbus.read_messages)
        shared_memory.backend_thread.start()

    @staticmethod
    def run_presentation():
        microsec_message(1, "Presentation started")
        shared_memory.root = tk.Tk()
        shared_memory.root.protocol("WM_DELETE_WINDOW", yesican_shutdown)
        shared_memory.root.config(cursor='none')

        if shared_memory.settings.get_fullscreen_state():
            shared_memory.root.wm_attributes('-fullscreen', 'True')
        shared_memory.root.geometry(
            str(shared_memory.settings.get_screen_width()) + "x" + str(shared_memory.settings.get_screen_height())
        )
        shared_memory.root.configure(bg=shared_memory.settings.get_bg_color())

        window = MainWindow(shared_memory.root)
        shared_memory.root.after(100, lambda: window.check_switch(shared_memory.root))
        shared_memory.root.mainloop()


if __name__ == "__main__":
    microsec_message(1, "YesICan " + __version__ + " starting")

    if platform.system() == 'Linux':
        shared_memory.is_linux_os = True
    elif platform.system() == 'Windows':
        shared_memory.is_linux_os = False
    else:
        microsec_message(1, "Unsupported platform")
        exit(0)

    presentation = Presentation()
    presentation.run_presentation()
