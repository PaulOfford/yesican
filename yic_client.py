import threading

from yic_gui import *

class YicClient:

    backend = None  # we need access to the backend object to retrieve CAN data
    be_t = None  # thread anchor

    def __init__(self):
        pass
        # start backend thread
        # self.backend = Backend()
        # self.be_t = threading.Thread(target=self.backend.backend_loop)
        # self.be_t.start()

    def process_updates(self):
        pass

    def client_shutdown(self):
        # ToDo: need to signal to the backend to stop

        # self.be_t.join(1)  # wait for up to one second for the backend thread to exit

        root.destroy()

    def run_client(self):

        # we need to ensure closing the window stops the backend
        root.protocol("WM_DELETE_WINDOW", self.client_shutdown)

        frame_container = tk.Frame(root)
        frame_container.pack(fill='both', expand=1, side='top', anchor='n')

        # frame_hdr = tk.Frame(frame_container, background="black", height=100, pady=10)
        # frame_hdr.pack(fill='x', side='top', anchor='n')
        # self.header = GuiHeader(header_frame=frame_hdr)  # populate the header
        #
        frame_main = tk.Frame(frame_container, pady=4)
        frame_main.pack(fill=tk.BOTH, expand=1, side='top', anchor='n', padx=4)

        # self.header.clock_tick()

        self.main = GuiMain(frame=frame_main)  # populate the main area

        # self.main.reload_qso_box()

        # self.main.reload_blog_list()

        root.after(200, self.process_updates)
        root.mainloop()


if __name__ == "__main__":
    c = YicClient()
    c.run_client()
