from tkinter import *
import tkinter.ttk as ttk
import threading
import time

root = Tk()
root.geometry("200x200")
root.title("Progress Bar Demo")

# Prepare the type of Progress bar needed (determinate or indeterminate mode)
processing_bar = ttk.Progressbar(root, orient='horizontal', mode='indeterminate')

# Place the bar at the centre of the window
processing_bar.place(relx=0.5, rely=0.5, anchor=CENTER)

# use processing_bar.stop() to stop it
processing_bar.start(30)
# Do something
processing_bar.stop()

root.mainloop()
