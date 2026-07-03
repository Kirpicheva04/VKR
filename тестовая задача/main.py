import tkinter as tk
from gui.main_window import HeatEquationGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = HeatEquationGUI(root)
    root.mainloop()