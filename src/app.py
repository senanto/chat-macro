import json
import os
import time
import tkinter as tk
from tkinter import ttk
import keyboard

APPDATA_FOLDER = os.path.join(os.getenv('APPDATA'), 'ChatMacro-Senanto')
CONFIG_FILE = os.path.join(APPDATA_FOLDER, 'config.json')

os.makedirs(APPDATA_FOLDER, exist_ok=True)

def load_data():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_macro():
    key = key_entry.get().strip()
    command = command_entry.get().strip()
    
    if key and command:
        data[key] = command
        save_data(data)
        key_entry.delete(0, tk.END)
        command_entry.delete(0, tk.END)
        update_listbox()

def delete_macro(key):
    if key in data:
        del data[key]
        save_data(data)
        update_listbox()

def update_listbox():
    listbox.delete(0, tk.END)
    for key, command in data.items():
        listbox.insert(tk.END, f"{key}: {command}")

def macro(event):
    key = event.name
    if key in data:
        command = data[key]
        keyboard.press('t') 
        time.sleep(0.1)
        keyboard.write(command)
        keyboard.press_and_release('enter')

root = tk.Tk()
root.iconbitmap('cms.ico')
root.title("CMS")

tab_control = ttk.Notebook(root)
add_tab = ttk.Frame(tab_control)
remove_tab = ttk.Frame(tab_control)

tab_control.add(add_tab, text="ADD")
tab_control.add(remove_tab, text="REMOVE")
tab_control.pack(expand=1, fill="both")

tk.Label(add_tab, text="Key:").grid(row=0, column=0, padx=5, pady=5)
key_entry = tk.Entry(add_tab)
key_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(add_tab, text="Command:").grid(row=1, column=0, padx=5, pady=5)
command_entry = tk.Entry(add_tab)
command_entry.grid(row=1, column=1, padx=5, pady=5)

add_button = tk.Button(add_tab, text="Add", command=add_macro)
add_button.grid(row=2, column=0, columnspan=2, pady=10)

listbox = tk.Listbox(remove_tab)
listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

delete_button = tk.Button(remove_tab, text="Delete", command=lambda: delete_macro(listbox.get(tk.ACTIVE).split(":")[0]))
delete_button.pack(pady=5)

data = load_data()
update_listbox()

keyboard.on_press(macro)

root.mainloop()
