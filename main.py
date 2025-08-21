import tkinter as tk
from gui import NewsGUI   # import GUI class

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsGUI(root)
    root.mainloop()
