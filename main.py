
import tkinter as tk

from interface import ChronoPicInterface
from config import APP_NAME


def main():

    root = tk.Tk()

    app = ChronoPicInterface(root)

    root.mainloop()


if __name__ == "__main__":
    main()
