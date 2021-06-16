import tkinter as tk
from tkinter import ttk
import tkinter.messagebox


##########################################################
# Start of Tkinter Code


# root window
root = tk.Tk()
root.eval('tk::PlaceWindow . center')
root.geometry("300x250")
root.resizable(False, False)
root.title('Site Details')


# store entries
Username_var = tk.StringVar()
password_var = tk.StringVar()
IP_Address_var = tk.StringVar()
Site_code_var = tk.StringVar()


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


# Submit button
Submit_button = ttk.Button(Site_details, text="Submit", command=root.destroy)
Submit_button.pack(fill='x', expand=True, pady=10)


root.attributes('-topmost', True)
root.mainloop()


username = Username_var.get()
password = password_var.get()
IP_Address = IP_Address_var.get()
Sitecode = Site_code_var.get()


def messagebox(text, title):
    message = tkinter.Tk()
    message.attributes('-topmost', True)
    message.withdraw()
    tkinter.messagebox.showinfo(title, text)
    message.destroy()

# End of Tkinter Code
##########################################################
