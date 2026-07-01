# CMS - Chat Macro System

A lightweight and customizable **Minecraft chat macro utility** for Windows.

CMS allows you to bind keyboard or mouse buttons to Minecraft chat commands, making repetitive commands fast and effortless. Whether you're playing on Survival, SkyBlock, Prison, Factions, or any other server, CMS helps automate commonly used chat commands without modifying the game.

---
## Download
[Download cms.exe](https://github.com/senanto/chat-macro/releases/download/v2/cms.exe)

## Preview

> Minimal interface built with Tkinter and a custom borderless Windows design.

<img width="497" height="576" alt="image" src="https://github.com/user-attachments/assets/46387a81-af3b-482a-8136-6ad616cc3f73" />
<img width="498" height="575" alt="image" src="https://github.com/user-attachments/assets/701168d0-eca3-42ba-9260-3231e5f8b6bb" />


---

## Features

* Keyboard and mouse keybind support
* Global hotkey detection
* One-click key recording
* Unlimited macro creation
* Edit and delete existing macros
* Automatic configuration saving
* Modern dark interface
* Custom frameless window
* Runs in the background
* Optional chat-state detection
* Preserves Caps Lock state automatically
* Lightweight with low memory usage

---

## Supported Commands

Examples:

```text
/home
/spawn
/warp mine
/msg Player Hello!
/hub
/shop
/sell
```

Any text that can normally be typed into Minecraft chat can be used as a macro.

---

## How It Works

1. Launch CMS.
2. Create a new macro.
3. Enter the command you want to send.
4. Record or select a keyboard or mouse button.
5. Join Minecraft.
6. Press your assigned key.

CMS will automatically:

* Open the chat (`T`)
* Type your command
* Press Enter
* Restore your previous Caps Lock state

---

## Configuration

Your macros are automatically stored in:

```text
%APPDATA%\ChatMacro-Senanto\config.json
```

No manual configuration is required.

---

## Requirements

* Windows 10 / Windows 11
* Python 3.10 or newer

Python dependencies:

```bash
pip install pynput sv-ttk
```

---

## Building

Clone the repository:

```bash
git clone https://github.com/senanto/chat-macro.git
cd chat-macro
```

Build the executable:

```bash
pyinstaller --onefile --windowed app.py
```

The compiled executable will be available inside the `dist` folder.

---

## Disclaimer

CMS simply automates keyboard input and does **not** modify Minecraft or inject into the game process.

Always make sure the use of macros is permitted on the server you are playing on. Some servers may prohibit automated input.

---

## License

This project is licensed under the **MIT License**.

Feel free to use, modify, distribute, and contribute under the terms of the MIT License.

---
