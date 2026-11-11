import time
import win32api
import win32con
import win32gui


def find_ds2_window():
    """Ищет окно Dark Souls II в любом регистре."""
    found_hwnd = None

    def callback(hwnd, _):
        nonlocal found_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "dark souls ii" in title.lower():
                found_hwnd = hwnd

    win32gui.EnumWindows(callback, None)
    return found_hwnd


def make_fast_borderless(hwnd):
    """Убирает рамки окна и предотвращает черный экран при Alt+Tab."""
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

    
    if style & (win32con.WS_CAPTION | win32con.WS_THICKFRAME): #стработат один раз 
        
        style &= ~(                             # 1) меняем стиль на чистый WS_POPUP (без заголовка и границ)
            win32con.WS_CAPTION
            | win32con.WS_THICKFRAME
            | win32con.WS_MINIMIZEBOX
            | win32con.WS_MAXIMIZEBOX
            | win32con.WS_SYSMENU
        )
        style |= win32con.WS_POPUP
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)    # 2) убираем системные отступы рамки винды
        ex_style &= ~(
            win32con.WS_EX_DLGMODALFRAME
            | win32con.WS_EX_CLIENTEDGE
            | win32con.WS_EX_STATICEDGE
            | win32con.WS_EX_WINDOWEDGE
        )
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        win32gui.SetWindowPos(          # 3) высота +1 пиксель не дает видеокарте перехватывать монитор в эксклюзивный режим
            hwnd,
            None,
            0,
            0,
            screen_width,
            screen_height + 1,
            win32con.SWP_FRAMECHANGED
            | win32con.SWP_NOZORDER
            | win32con.SWP_NOOWNERZORDER
            | win32con.SWP_SHOWWINDOW,
        )
        return True
    return False


if __name__ == "__main__":
    print(
        "Ожидание запуска Dark Souls II (убедитесь, что в игре включен режим 'В окне')..."
    )
    while True:
        hwnd = find_ds2_window()
        if hwnd:
            if make_fast_borderless(hwnd):
                print(
                    "Готово! Рамки убраны, быстрый Alt+Tab активирован."
                )
        time.sleep(1.5)