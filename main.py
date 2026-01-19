# main.py
import tkinter as tk
from App import TemperedWindows
from utils import relaunch_as_admin


if __name__ == "__main__":
    relaunch_as_admin()
    root = tk.Tk()
    app = TemperedWindows(root)
    root.mainloop()

