from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import sleep
import threading


def task(tk_root):
    label = Label(tk_root, text='Progress Bar', font = "50")
    label.pack(pady=5)

    progress_bar = ttk.Progressbar(tk_root, orient=HORIZONTAL, length=220, mode="indeterminate")
    progress_bar.pack(pady=20)

    progress_bar.start()

    tk_root.geometry("300x150")
    tk_root.title("PythonLobby.com")
    tk_root.mainloop()


def process_of_unknown_duration(tk_root):
    sleep(5)
    print('Done')
    tk_root.destroy()



root = Tk()
t1 = threading.Thread(target=process_of_unknown_duration, args=(root,), daemon=True)
t1.start()
task(root)  # This will block while the mainloop runs
# t1.join()

# hide main window
msg_box = Tk()
msg_box.withdraw()

# message box display
messagebox.showinfo("Information", "Informative message")


