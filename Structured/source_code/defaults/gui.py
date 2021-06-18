import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
from tkinter import filedialog

# root window
root = tk.Tk()
root.eval('tk::PlaceWindow . center')
root.geometry("300x400")
root.resizable(False, False)
root.title('Site Details')


# store entries
Username_var = tk.StringVar()
password_var = tk.StringVar()
IP_Address_var = tk.StringVar()
Site_code_var = tk.StringVar()
Debugging_var = tk.IntVar()


# Site details frame
Site_details = ttk.Frame(root)
Site_details.pack(padx=10, pady=10, fill='x', expand=True)


# Username
Username_label = ttk.Label(Site_details, text="Username:")
Username_label.pack(fill='x', expand=True)
Username_entry = ttk.Entry(Site_details, textvariable=Username_var)
Username_entry.pack(fill='x', expand=True)
Username_entry.focus()


# Password
password_label = ttk.Label(Site_details, text="Password:")
password_label.pack(fill='x', expand=True)
password_entry = ttk.Entry(Site_details, textvariable=password_var, show="*")
password_entry.pack(fill='x', expand=True)


# ip Address
IP_Address_label = ttk.Label(Site_details, text="IP Address:")
IP_Address_label.pack(fill='x', expand=True)
IP_Address_entry = ttk.Entry(Site_details, textvariable=IP_Address_var)
IP_Address_entry.pack(fill='x', expand=True)


# Site Code
Site_code_label = ttk.Label(Site_details, text="Site code:")
Site_code_label.pack(fill='x', expand=True)
Site_code_entry = ttk.Entry(Site_details, textvariable=Site_code_var)
Site_code_entry.pack(fill='x', expand=True)

# Debugging
Debugging_label = ttk.Label(Site_details, text="Debugging (0 = OFF, 1 = ON):")
Debugging_label.pack(fill='x', expand=True)
Debugging_entry = ttk.Entry(Site_details, textvariable=Debugging_var)
Debugging_entry.pack(fill='x', expand=True)


# Open file dialog button
def get_filename():
    open_dialog = filedialog.askopenfilename(parent=root, initialdir='.', title='Choose an excel file')
    resultLabel.config(text=open_dialog)
    return open_dialog


open_file = ttk.Button(Site_details, text='Open a File', width=15, command=get_filename)
open_file.pack(expand=True, pady=10)

resultLabel = ttk.Label(Site_details, text="", wraplength=300)
resultLabel.pack(fill='x', expand=True)

# Submit button
Submit_button = ttk.Button(Site_details, text="Submit", command=root.destroy)
Submit_button.pack(fill='x', pady=10)


root.attributes('-topmost', True)
root.mainloop()


username = Username_var.get()
password = password_var.get()
IP_Address = IP_Address_var.get()
Sitecode = Site_code_var.get()
Debugging = Debugging_var.get()


def messagebox(text, title):
    message = tkinter.Tk()
    message.attributes('-topmost', True)
    message.withdraw()
    tkinter.messagebox.showinfo(title, text)
    message.destroy()
