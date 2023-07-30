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
print("============================================\n     Wpisz 'STOP' aby zatrzymać program\n     Wpisz 'HIDE' aby ukryć program\n============================================\n\n           V DZIENNIK TEKSTOWY V\n--------------------------------------------\n")

# Zmienna do przechowywania stanu ukrywania okna
window_hidden = True

def log_status(status_message, colored_message):
    # Pobierz aktualną datę i godzinę
    timestamp = datetime.now().strftime("|%Y-%m-%d| [%H:%M:%S]")

    # Wypisz kolorowany komunikat w konsoli
    print(f"{timestamp}: "+colored_message)

    # Zapisz komunikat do pliku "internet_status.txt"
    with open("internet_status.txt", "a") as f:
        f.write(f"{timestamp}: {status_message}\n")

def check_ethernet_connection():
    last_status = None  # Zmienna do przechowywania ostatniego znanego stanu połączenia
    ethernet_interface = "Ethernet"  # Nazwa interfejsu ethernetowego (może być inna w zależności od systemu)

    while True:
        interfaces = psutil.net_if_stats()

        # Sprawdź, czy interfejs ethernetowy jest aktywny
        if ethernet_interface in interfaces and interfaces[ethernet_interface].isup:
            try:
                # Sprawdź, czy można nawiązać połączenie z adresem IP XXX na porcie 53

                #XXX Zmień swój adres ip ethernetu zależnie od tego jaki masz ustawiony XXX

                socket.create_connection(("8.8.8.8", 53), timeout=5)
                socket.create_connection(("1.1.1.1", 53), timeout=5)
                socket.create_connection(("1.0.0.1", 53), timeout=5)

                # Połączenie sieciowe jest aktywne
                current_status = "{NET} Dobry"
                colored_status = colored(current_status, "light_green")

            except socket.error:
                # W przypadku braku połączenia
                current_status = "{NET} Słabszy"
                colored_status = colored(current_status, "light_red")
        else:
            current_status = "\n{Brak Połączenia}============================================\n"
            colored_status = colored(current_status, "red")

        if current_status != last_status:
            # Wypisz komunikat w konsoli i zapisz do pliku, tylko jeśli stan się zmienił
            log_status(current_status, colored_status)

        last_status = current_status


# Funkcja do minimalizowania lub przywracania okna konsoli
def toggle_window(icon, item):
    global window_hidden
    console_handle = ctypes.windll.kernel32.GetConsoleWindow()
    console_visible = ctypes.windll.user32.IsWindowVisible(console_handle)

    if console_visible:
        ctypes.windll.user32.ShowWindow(console_handle, 0)  # Minimalizuj okno konsoli
        window_hidden = True
    else:
        ctypes.windll.user32.ShowWindow(console_handle, 5)  # Przywróć okno konsoli
        window_hidden = False

    # Zaktualizuj menu w zasobniku systemowym na podstawie aktualnego stanu okna konsoli
    update_system_tray_menu(icon)

# Funkcja do pokazywania/ukrywania konsoli po kliknięciu w ikonkę zasobnika systemowego lub wpisaniu "hide" w konsoli
def on_tray_icon_click(icon, item):
    if item.text == "Pokaż / Ukryj konsolę":
        toggle_window(icon, item)
    elif item.text == "Pokaż / Ukryj konsolę":
        toggle_window(icon, item)
    elif item.text == "Zakończ":
        icon.stop()
        os._exit(0)  # Wymuszenie zamknięcia programu

# Funkcja do aktualizacji menu w zasobniku systemowym na podstawie aktualnego stanu okna konsoli
def update_system_tray_menu(icon):
    global window_hidden

    menu_items = [
        MenuItem("Pokaż / Ukryj konsolę", on_tray_icon_click) if not window_hidden else MenuItem("Pokaż / Ukryj konsolę", on_tray_icon_click),
        MenuItem("Zakończ", on_tray_icon_click)
    ]

    # Utwórz nowy obiekt Menu i przypisz go do atrybutu menu dla ikony
    icon.menu = Menu(*menu_items)

# Utwórz ikonę dla zasobnika systemowego
icon_image = Image.open("icon.png")

menu = Menu(MenuItem("Pokaż / Ukryj konsolę", on_tray_icon_click), MenuItem("Zakończ", on_tray_icon_click))

icon = Icon("[SCRIPT] Stan Internetu", icon_image, "[SCRIPT] Stan Internetu", menu)

# Uruchom funkcję check_ethernet_connection() w tle
thread = threading.Thread(target=check_ethernet_connection)
thread.daemon = True
thread.start()

# Zaktualizuj menu w zasobniku systemowym
update_system_tray_menu(icon)

# Uruchom icon.run() w oddzielnym wątku, aby obsłużyć zdarzenia zasobnika systemowego
icon_thread = threading.Thread(target=icon.run)
icon_thread.daemon = True
icon_thread.start()

# Utrzymuj działanie głównego wątku, aby obsługiwać wprowadzanie w konsoli
try:
    while True:
        command = getpass.getpass("")  # Używamy getpass.getpass zamiast input, aby ukryć wprowadzane polecenie
        command = command.upper().strip()
        if command == "STOP":
            break
        elif command == "HIDE":
            toggle_window(icon, None)  # Ukryj okno konsoli
        else:
            print("[Błąd] Nieznana komenda\n")
except KeyboardInterrupt:
    pass
