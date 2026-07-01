import json
import os
import time
import tkinter as tk
from tkinter import ttk
import sv_ttk
import threading
import ctypes
from pynput import mouse
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Key, Controller, Listener

user32 = ctypes.WinDLL('user32', use_last_error=True)
VK_CAPITAL = 0x14

def is_capslock_on():
    return (user32.GetKeyState(VK_CAPITAL) & 1) != 0

def set_capslock(state):
    if state == is_capslock_on():
        return
    user32.keybd_event(VK_CAPITAL, 0, 0, 0)
    user32.keybd_event(VK_CAPITAL, 0, 2, 0)

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

data = load_data()
in_chat = False
editing_key = None
is_editing = False
controller = Controller()

def add_macro():
    global is_editing, editing_key
    key = current_key.get()
    command = command_entry.get().strip()
    if not key or key == "None" or not command:
        return
    if is_editing and editing_key:
        if editing_key in data:
            del data[editing_key]
        data[key] = command
        is_editing = False
        editing_key = None
        add_button.config(text="Add")
    else:
        data[key] = command
    save_data(data)
    current_key.set("None")
    command_entry.delete(0, tk.END)
    update_listbox()

def delete_macro():
    selected = listbox.get(tk.ACTIVE)
    if selected:
        key = selected.split(" ")[0].strip()
        if key in data:
            del data[key]
            save_data(data)
            update_listbox()

def edit_macro():
    global is_editing, editing_key
    selected = listbox.get(tk.ACTIVE)
    if not selected:
        return
    key = selected.split(" ")[0].strip()
    if key not in data:
        return
    is_editing = True
    editing_key = key
    current_key.set(key)
    command_entry.delete(0, tk.END)
    command_entry.insert(0, data[key])
    add_button.config(text="Update")
    tab_control.select(add_tab)

def update_listbox():
    listbox.delete(0, tk.END)
    for key, command in data.items():
        listbox.insert(tk.END, f"{key}  │  {command}")

def execute_macro(key_name):
    if not enabled_var.get():
        return
    if not work_on_chat_var.get() and in_chat:
        return
    if key_name in data:
        command = data[key_name]
        caps_was_on = is_capslock_on()
        if caps_was_on:
            set_capslock(False)
            time.sleep(0.05)
        controller.press('t')
        time.sleep(0.05)
        controller.type(command)
        controller.press(Key.enter)
        controller.release(Key.enter)
        if caps_was_on:
            set_capslock(True)

def on_key_press(key):
    global in_chat
    try:
        key_name = key.char.lower()
    except AttributeError:
        key_name = key.name.lower()
    if key_name == 't':
        in_chat = True
    elif key_name in ('enter', 'esc'):
        in_chat = False
    execute_macro(key_name)

def on_mouse_click(x, y, button, pressed):
    if pressed:
        btn_name = str(button).split('.')[-1]
        execute_macro(f"mouse_{btn_name}")

recording = False
recorded_key = None

def start_recording():
    global recording, recorded_key
    if recording:
        return
    recording = True
    recorded_key = None
    current_key.set("Press any key or click mouse...")
    threading.Thread(target=record_input, daemon=True).start()

def record_input():
    global recording, recorded_key
    recorded_key = None
    stop_event = threading.Event()

    def on_click(x, y, button, pressed):
        if pressed and recording:
            global recorded_key
            btn_name = str(button).split('.')[-1]
            recorded_key = f"mouse_{btn_name}"
            stop_event.set()
            return False

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    def on_key_press_record(key):
        if recording:
            global recorded_key
            try:
                recorded_key = key.char.lower()
            except AttributeError:
                recorded_key = key.name.lower()
            stop_event.set()
            return False

    keyboard_listener = Listener(on_press=on_key_press_record)
    keyboard_listener.start()

    stop_event.wait()
    mouse_listener.stop()
    keyboard_listener.stop()
    root.after(0, finish_recording)

def finish_recording():
    global recording
    recording = False
    if recorded_key:
        current_key.set(recorded_key)
    else:
        current_key.set("None")

GWL_STYLE = -16
GWL_EXSTYLE = -20
WS_BORDER = 0x00800000
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_DLGFRAME = 0x00400000
WS_SYSMENU = 0x00080000
WS_MINIMIZEBOX = 0x00020000
WS_MAXIMIZEBOX = 0x00010000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00040000
WS_EX_WINDOWEDGE = 0x00000100
WS_EX_CLIENTEDGE = 0x00000200
SWP_FRAMECHANGED = 0x0020
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_SHOWWINDOW = 0x0040
SWP_NOACTIVATE = 0x0010
WM_SYSCOMMAND = 0x0112
SC_MINIMIZE = 0xF020

hwnd = None

def get_hwnd():
    """Gerçek Windows pencere handle'ını al"""
    global hwnd
    if hwnd is None or hwnd == 0:
        tk_id = root.winfo_id()
        hwnd = ctypes.windll.user32.GetParent(tk_id)
        if hwnd == 0:
            hwnd = tk_id
    return hwnd

def make_borderless_taskbar():
    """
    Pencereyi borderless yap ama taskbar'da görünür kal.
    Çözüm: Normal pencere oluştur, sonra API ile border'ları kaldır.
    """
    h = get_hwnd()
    if not h:
        root.after(100, make_borderless_taskbar)
        return

    style = ctypes.windll.user32.GetWindowLongW(h, GWL_STYLE)
    exstyle = ctypes.windll.user32.GetWindowLongW(h, GWL_EXSTYLE)

    style &= ~(WS_CAPTION | WS_THICKFRAME | WS_DLGFRAME | WS_BORDER | 
               WS_MAXIMIZEBOX)
    style |= WS_MINIMIZEBOX | WS_SYSMENU
    exstyle &= ~WS_EX_TOOLWINDOW
    exstyle |= WS_EX_APPWINDOW
    exstyle &= ~(WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE)

    ctypes.windll.user32.SetWindowLongW(h, GWL_STYLE, style)
    ctypes.windll.user32.SetWindowLongW(h, GWL_EXSTYLE, exstyle)

    ctypes.windll.user32.SetWindowPos(
        h, 0, 0, 0, 0, 0,
        SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | 
        SWP_NOACTIVATE | SWP_SHOWWINDOW
    )

def minimize_window():
    """Pencereyi taskbar'a minimize et"""
    root.wm_iconify()

def close_window():
    root.destroy()

def start_move(event):
    global x, y
    x = event.x
    y = event.y

def on_move(event):
    deltax = event.x - x
    deltay = event.y - y
    new_x = root.winfo_x() + deltax
    new_y = root.winfo_y() + deltay
    root.geometry(f"+{new_x}+{new_y}")


root = tk.Tk()
root.overrideredirect(True)
root.title("CMS")
root.geometry("400x460")
root.resizable(False, False)


sv_ttk.set_theme("dark")

root.after(200, make_borderless_taskbar)

root.after(300, lambda: (root.wm_withdraw(), root.after(50, root.wm_deiconify)))

title_frame = ttk.Frame(root)
title_frame.pack(fill=tk.X, pady=(0,5))

title_label = ttk.Label(title_frame, text="CMS - github.com/senanto", font=("Segoe UI", 10, "bold"))
title_label.pack(side=tk.LEFT, padx=10)

title_frame.bind("<Button-1>", start_move)
title_frame.bind("<B1-Motion>", on_move)
title_label.bind("<Button-1>", start_move)
title_label.bind("<B1-Motion>", on_move)

btn_frame_title = ttk.Frame(title_frame)
btn_frame_title.pack(side=tk.RIGHT, padx=5)

min_btn = ttk.Button(btn_frame_title, text="─", width=3, command=minimize_window)
min_btn.pack(side=tk.LEFT, padx=2)

close_btn = ttk.Button(btn_frame_title, text="✕", width=3, command=close_window)
close_btn.pack(side=tk.LEFT, padx=2)

main_frame = ttk.Frame(root, padding=15)
main_frame.pack(fill=tk.BOTH, expand=True)

current_key = tk.StringVar(value="None")

top_frame = ttk.Frame(main_frame)
top_frame.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)

enabled_var = tk.BooleanVar(value=True)
enabled_check = ttk.Checkbutton(top_frame, text="Enabled", variable=enabled_var)
enabled_check.pack(side=tk.LEFT)

sep = ttk.Label(top_frame, text="│", padding=(5,0))
sep.pack(side=tk.LEFT)

work_on_chat_var = tk.BooleanVar(value=False)
work_check = ttk.Checkbutton(top_frame, text="Work on Chat", variable=work_on_chat_var)
work_check.pack(side=tk.LEFT)

tab_control = ttk.Notebook(main_frame)
add_tab = ttk.Frame(tab_control)
list_tab = ttk.Frame(tab_control)
tab_control.add(add_tab, text="Config")
tab_control.add(list_tab, text="List")
tab_control.pack(expand=1, fill="both")

ttk.Label(add_tab, text="Set Command (ex: /home)", anchor="w").pack(fill=tk.X, padx=5, pady=(10,0))
command_entry = ttk.Entry(add_tab)
command_entry.pack(fill=tk.X, padx=5, pady=5)

ttk.Label(add_tab, text="Set Keybind", anchor="w").pack(fill=tk.X, padx=5, pady=(15,0))
key_label = ttk.Label(add_tab, textvariable=current_key, relief="sunken", anchor="w")
key_label.pack(fill=tk.X, padx=5, pady=5)

record_btn = ttk.Button(add_tab, text="Record", command=start_recording)
record_btn.pack(fill=tk.X, padx=5, pady=5)

add_button = ttk.Button(add_tab, text="Add", command=add_macro)
add_button.pack(fill=tk.X, padx=5, pady=5)

listbox_frame = ttk.Frame(list_tab)
listbox_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

listbox = tk.Listbox(listbox_frame, bg="#1e1e1e", fg="white", selectbackground="#0078d7", 
                     borderwidth=0, highlightthickness=0, font=("Segoe UI", 9))
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)

btn_frame = ttk.Frame(list_tab)
btn_frame.pack(pady=5, fill=tk.X)

delete_button = ttk.Button(btn_frame, text="Delete", command=delete_macro)
delete_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

edit_button = ttk.Button(btn_frame, text="Edit", command=edit_macro)
edit_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

update_listbox()

keyboard_listener = Listener(on_press=on_key_press)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_mouse_click)
mouse_listener.start()

root.mainloop()
