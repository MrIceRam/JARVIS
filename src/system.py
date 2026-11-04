"""Работа с Windows: окна, клавиши, мышь, скриншоты, звук, автозапуск."""

import ctypes
import time
import winsound
from collections.abc import Iterator
from contextlib import contextmanager
from ctypes import wintypes
from pathlib import Path

import pyautogui
import pygetwindow
from PIL import Image, ImageGrab

from src import paths

ERROR_ALREADY_EXISTS = 183
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP = 0x0002, 0x0004
WINDOW_MINIMIZED = 7  # окно консоли открывается свёрнутым на панель задач

# Страховка pyautogui: падать, если мышь в углу экрана. Джарвису мешает — ты можешь быть вообще не за компьютером.
pyautogui.FAILSAFE = False


def already_running() -> bool:
    """Занимает системную метку "Jarvis". Если её уже держит другой процесс — вернёт True.

    Windows снимает метку сама, когда процесс завершается, даже при сбое.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW(None, False, "JarvisAssistant")
    return ctypes.get_last_error() == ERROR_ALREADY_EXISTS


def play_sound(path: Path) -> None:
    """Проиграть .wav и не ждать окончания."""
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


def process_name(window: pygetwindow.Win32Window) -> str:
    """Имя программы, которой принадлежит окно: "cs2.exe". Пустая строка, если Windows не дала узнать."""
    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.OpenProcess.restype = wintypes.HANDLE

    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(wintypes.HWND(window._hWnd), ctypes.byref(pid))
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        path = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(path))
        kernel32.QueryFullProcessImageNameW(wintypes.HANDLE(handle), 0, path, ctypes.byref(size))
        return Path(path.value).name.lower()
    finally:
        kernel32.CloseHandle(wintypes.HANDLE(handle))


def find_window(title_part: str, process: str | None = None) -> pygetwindow.Win32Window | None:
    """Первое видимое окно, в заголовке которого есть title_part (регистр не важен).

    Для игр передавай process: одного заголовка мало. "Counter-Strike 2" бывает и у окна Steam,
    а "Dota 2" — у вкладки браузера.
    """
    title_part = title_part.lower()
    for window in pygetwindow.getAllWindows():
        if window.visible and title_part in window.title.lower():
            if process is None or process_name(window) == process.lower():
                return window
    return None


def focus(window: pygetwindow.Win32Window) -> None:
    if window.isActive:
        return
    if window.isMinimized:
        window.restore()
    # Windows не даёт фоновому процессу забирать фокус. Обходной путь — "нажать" Alt перед переключением.
    pyautogui.press("alt")
    try:
        window.activate()
    except pygetwindow.PyGetWindowException:
        pass  # pygetwindow иногда кидает "Error code 0 - The operation completed successfully", хотя всё переключилось


@contextmanager
def focused(window: pygetwindow.Win32Window) -> Iterator[None]:
    """Внутри `with` окно активно. На выходе, даже при ошибке, возвращается предыдущее окно."""
    previous = pygetwindow.getActiveWindow()
    focus(window)
    time.sleep(0.3)  # даём окну время активироваться
    try:
        yield
    finally:
        time.sleep(0.1)
        if previous is not None and previous._hWnd != window._hWnd:
            focus(previous)


def press_key(key: str) -> None:
    pyautogui.press(key)


def capture(window: pygetwindow.Win32Window) -> Image.Image:
    """Скриншот окна. all_screens — чтобы окно на втором мониторе тоже попадало в кадр."""
    box = (window.left, window.top, window.left + window.width, window.top + window.height)
    return ImageGrab.grab(bbox=box, all_screens=True)


def click(x: int, y: int) -> None:
    """Клик левой кнопкой в координатах всего рабочего стола, потом мышь возвращается на место.

    Через WinAPI, а не pyautogui: тот знает размер только основного монитора.
    """
    user32 = ctypes.windll.user32
    cursor = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(cursor))

    user32.SetCursorPos(x - 3, y)  # игра подсвечивает кнопку, только когда мышь по ней двигается
    time.sleep(0.05)
    user32.SetCursorPos(x, y)
    time.sleep(0.15)
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.1)

    user32.SetCursorPos(cursor.x, cursor.y)


def autostart_enabled(link: Path = paths.STARTUP_LINK) -> bool:
    return link.exists()


def enable_autostart(link: Path = paths.STARTUP_LINK) -> None:
    """Создаёт ярлык Джарвиса в папке автозагрузки Windows."""
    import comtypes.client

    shell = comtypes.client.CreateObject("WScript.Shell", dynamic=True)
    shortcut = shell.CreateShortcut(str(link))
    shortcut.TargetPath = str(paths.JARVIS_EXE)
    shortcut.WorkingDirectory = str(paths.PROJECT_ROOT)
    shortcut.WindowStyle = WINDOW_MINIMIZED
    shortcut.Description = "Голосовой помощник Джарвис"
    shortcut.Save()


def disable_autostart(link: Path = paths.STARTUP_LINK) -> None:
    link.unlink(missing_ok=True)
