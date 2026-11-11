import ctypes
import os
import tkinter as tk
import keyboard
import win32con
import win32gui

SAVE_FILE = "ds2_deaths.txt"

HOTKEY_ADD = "f1"  # +1 смерть
HOTKEY_SUB = "f2"  # -1 смерть
HOTKEY_TOGGLE = "f3"  # показать/скрыть 
HOTKEY_RESET = "f4"  # сбросить счетчик на 0
HOTKEY_EXIT = "f10"  # полностью выключить скрипт


def find_ds2_window():
    """Проверяет, запущена ли игра Dark Souls II."""
    found_hwnd = None

    def callback(hwnd, _):
        nonlocal found_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "dark souls ii" in title.lower():
                found_hwnd = hwnd

    win32gui.EnumWindows(callback, None)
    return found_hwnd


class DS2CounterOnly:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DS2 Death Counter")

        self.root.geometry("+30+50")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.config(bg="black")
        self.root.wm_attributes("-transparentcolor", "black")

        self.make_clickthrough()

        self.deaths = self.load_deaths()
        self.is_visible = False
        self.force_show = False
        self.is_ds2_focused = False

        self.label = tk.Label(
            self.root,
            text=f"Смертей: {self.deaths}",
            font=("Impact", 26),
            fg="#b81d13",
            bg="black",
        )
        self.label.pack()

        # привязываем кнопки
        keyboard.add_hotkey(HOTKEY_ADD, self.increment_deaths)
        keyboard.add_hotkey(HOTKEY_SUB, self.decrement_deaths)
        keyboard.add_hotkey(HOTKEY_TOGGLE, self.toggle_force_show)
        keyboard.add_hotkey(HOTKEY_RESET, self.reset_deaths)
        keyboard.add_hotkey(HOTKEY_EXIT, self.close_app)

        print("Счетчик запущен!")
        print("[F1] +1 | [F2] -1 | [F3] Показать/Скрыть | [F4] Сброс на 0 | [F10] Выход")

        self.track_window_loop()

    def make_clickthrough(self):
        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style = (
            style
            | win32con.WS_EX_LAYERED
            | win32con.WS_EX_TRANSPARENT
            | win32con.WS_EX_TOOLWINDOW
        )
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

    def load_deaths(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    return int(f.read().strip())
            except ValueError:
                return 0
        else:
            self.save_deaths(0)
            return 0

    def save_deaths(self, count):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                f.write(str(count))
        except Exception as e:
            print(f"Ошибка сохранения: {e}")

    def update_ui(self):
        self.label.config(text=f"Смертей: {self.deaths}")

    def increment_deaths(self):
        if self.is_ds2_focused or self.force_show:
            self.deaths += 1
            self.save_deaths(self.deaths)
            self.root.after(0, self.update_ui)

    def decrement_deaths(self):
        if (self.is_ds2_focused or self.force_show) and self.deaths > 0:
            self.deaths -= 1
            self.save_deaths(self.deaths)
            self.root.after(0, self.update_ui)

    def reset_deaths(self):
        """Сбрасывает счетчик смертей на 0 по нажатию F4."""
        if self.is_ds2_focused or self.force_show:
            self.deaths = 0
            self.save_deaths(0)
            self.root.after(0, self.update_ui)

    def toggle_force_show(self):
        self.force_show = not self.force_show

    def close_app(self):
        """Полностью выключает скрипт по нажатию F10."""
        print("Выключение счетчика...")
        self.root.after(0, self.root.destroy)
        os._exit(0)

    def track_window_loop(self):
        ds2_hwnd = find_ds2_window()

        if ds2_hwnd:
            foreground_hwnd = win32gui.GetForegroundWindow()
            self.is_ds2_focused = foreground_hwnd == ds2_hwnd
        else:
            self.is_ds2_focused = False

        should_show = self.is_ds2_focused or self.force_show

        if should_show:
            if not self.is_visible:
                self.root.geometry("+30+50")
                self.root.deiconify()
                self.root.wm_attributes("-topmost", True)
                self.is_visible = True
        else:
            if self.is_visible:
                self.root.withdraw()
                self.is_visible = False

        self.root.after(100, self.track_window_loop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DS2CounterOnly()
    app.run()