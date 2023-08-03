import threading
import psutil
import socket
import os
import ctypes
from datetime import datetime
from pystray import Icon, Menu, MenuItem
from PIL import Image
from termcolor import colored
import msvcrt
import getpass

os.system("mode con: cols=44 lines=30")
print("============================================\n     Type 'STOP' to close the program\n     Type 'HIDE' to hide the program\n============================================\n\n                STATUS LOG\n--------------------------------------------\n")

# Variable to store window hide/show state
window_hidden = True

def log_status(status_message, colored_message):
    timestamp = datetime.now().strftime("|%Y-%m-%d| [%H:%M:%S]")
    print(f"{timestamp}: " + colored_message)
    with open("internet_status.txt", "a") as f:
        f.write(f"{timestamp}: {status_message}\n")

def check_ethernet_connection():
    last_status = None
    ethernet_interface = "Ethernet"

    while True:
        interfaces = psutil.net_if_stats()

        if ethernet_interface in interfaces and interfaces[ethernet_interface].isup:
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=5)
                socket.create_connection(("1.1.1.1", 53), timeout=5)
                socket.create_connection(("1.0.0.1", 53), timeout=5)
                current_status = "{NET} GOOD"
                colored_status = colored(current_status, "light_green")
            except socket.error:
                current_status = "{NET} WEAKER"
                colored_status = colored(current_status, "light_red")
        else:
            current_status = "\n{NO CONNECTION}============================================\n"
            colored_status = colored(current_status, "red")

        if current_status != last_status:
            log_status(current_status, colored_status)

        last_status = current_status

def toggle_window(icon, item):
    global window_hidden
    console_handle = ctypes.windll.kernel32.GetConsoleWindow()
    console_visible = ctypes.windll.user32.IsWindowVisible(console_handle)

    if console_visible:
        ctypes.windll.user32.ShowWindow(console_handle, 0)
        window_hidden = True
    else:
        ctypes.windll.user32.ShowWindow(console_handle, 5)
        window_hidden = False

    update_system_tray_menu(icon)

def on_tray_icon_click(icon, item):
    if item.text == "Show / Hide Console":
        toggle_window(icon, item)
    elif item.text == "Exit":
        icon.stop()
        os._exit(0)

def update_system_tray_menu(icon):
    global window_hidden

    menu_items = [
        MenuItem("Show / Hide Console", on_tray_icon_click) if not window_hidden else MenuItem("Show / Hide Console", on_tray_icon_click),
        MenuItem("Exit", on_tray_icon_click)
    ]

    icon.menu = Menu(*menu_items)

icon_image = Image.open("icon.png")

menu = Menu(MenuItem("Show / Hide Console", on_tray_icon_click), MenuItem("Exit", on_tray_icon_click))

icon = Icon("[SCRIPT] Internet Status", icon_image, "[SCRIPT] Internet Status", menu)

thread = threading.Thread(target=check_ethernet_connection)
thread.daemon = True
thread.start()

update_system_tray_menu(icon)

icon_thread = threading.Thread(target=icon.run)
icon_thread.daemon = True
icon_thread.start()

try:
    while True:
        command = getpass.getpass("")
        command = command.upper().strip()
        if command == "STOP":
            break
        elif command == "HIDE":
            toggle_window(icon, None)
        else:
            print("[Error] Unknown command\n")
except KeyboardInterrupt:
    pass
