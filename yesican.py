from gui import *

if __name__ == "__main__":
    settings = Settings()
    root = tk.Tk()
    root.geometry(str(settings.screen_width) + "x" + str(settings.screen_height))
    root.configure(bg=settings.bg_color)
    pit = GuiGearShift(window_root=root)
    pit.render_screen()
