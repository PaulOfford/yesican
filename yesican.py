import threading

import shared_memory
from settings import *
from gui import *
from backend import *

import switcher


def yesican_shutdown():
    shared_memory.run_state = shared_memory.RUN_STATE_AWAITING_BACKEND
    shared_memory.backend_thread.join(0.5)  # wait for up to one second for the backend thread to exit
    shared_memory.root.destroy()
    shared_memory.run_state = shared_memory.RUN_STATE_EXITING
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

    def change_window(self):
        self.frameList[self.index].forget()
        self.index = (self.index + 1) % len(self.frameList)
        self.frameList[self.index].tkraise()
        self.frameList[self.index].pack()
        self.visible = True

        shared_memory.current_mode = shared_memory.desired_mode

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
                shared_memory.desired_mode = 1
                shared_memory.pit_speed_switch = True

        if shared_memory.current_mode != shared_memory.desired_mode:
            self.change_window()
        if shared_memory.flash_window and shared_memory.current_mode < len(self.frameList) - 1:
            self.flash_window(flash=True)
        elif not self.visible:
            self.flash_window(flash=False)
        master.after(250, lambda: self.check_switch(master))


class Presentation:

    def __init__(self):
        shared_memory.settings = Settings()
        shared_memory.settings.read_config()

        # start backend thread
        backend = Backend()
        shared_memory.backend_thread = threading.Thread(target=backend.backend_loop)
        shared_memory.backend_thread.start()

    def run_presentation(self):
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
    if platform.system() == 'Linux':
        shared_memory.is_linux_os = True
    elif platform.system() == 'Windows':
        shared_memory.is_linux_os = False
    else:
        print("Unsupported platform")
        exit(0)

    presentation = Presentation()
    presentation.run_presentation()
