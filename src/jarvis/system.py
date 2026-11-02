"""Работа с Windows: окна, клавиши, звук."""

import time
import winsound
from pathlib import Path

import pyautogui
import pygetwindow


def play_sound(path: Path) -> None:
    """Проиграть .wav и не ждать окончания."""
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)


def find_window(title_part: str) -> pygetwindow.Win32Window | None:
    """Первое видимое окно, в заголовке которого есть title_part (регистр не важен)."""
    title_part = title_part.lower()
    for window in pygetwindow.getAllWindows():
        if window.visible and title_part in window.title.lower():
            return window
    return None


def focus(window: pygetwindow.Win32Window) -> None:
    if window.isMinimized:
        window.restore()
    # Windows не даёт фоновому процессу забирать фокус. Обходной путь — "нажать" Alt перед переключением.
    pyautogui.press("alt")
    try:
        window.activate()
    except pygetwindow.PyGetWindowException:
        pass  # pygetwindow иногда кидает "Error code 0 - The operation completed successfully", хотя всё переключилось


def press_key_in_window(title_part: str, key: str) -> bool:
    """Переключиться на окно, нажать клавишу и вернуться в предыдущее окно.

    Возвращает False, если окно не найдено.
    """
    target = find_window(title_part)
    if target is None:
        return False

    previous = pygetwindow.getActiveWindow()
    focus(target)
    time.sleep(0.3)  # даём окну время активироваться
    pyautogui.press(key)
    time.sleep(0.1)

    if previous is not None and previous._hWnd != target._hWnd:
        focus(previous)
    return True
