"""Принять найденную игру. В Dota 2 это Enter, в CS2 только клик по зелёной кнопке."""

import pygetwindow

from jarvis import paths
from jarvis.core import CommandError, CommandRegistry
from jarvis.system import capture, click, find_window, focused, press_key
from jarvis.vision import find_green_button


def find_game(title: str, process: str) -> pygetwindow.Win32Window:
    window = find_window(title, process)
    if window is None:
        raise CommandError(f"Не нашёл окно {title}")
    return window


def click_green_button(window: pygetwindow.Win32Window) -> None:
    """Найти кнопку на скриншоте окна и кликнуть. Скриншот не зависит от монитора и разрешения."""
    with focused(window):
        screenshot = capture(window)
        button = find_green_button(screenshot)
        if button is None:
            # Сохраняем, что видел Джарвис: по этой картинке понятно, почему кнопка не нашлась
            paths.DEBUG_SCREENSHOT.parent.mkdir(exist_ok=True)
            screenshot.save(paths.DEBUG_SCREENSHOT)
            raise CommandError("Не вижу кнопку Принять")
        click(window.left + button[0], window.top + button[1])


def accept_dota() -> None:
    with focused(find_game("Dota 2", "dota2.exe")):
        press_key("enter")


def accept_cs() -> None:
    click_green_button(find_game("Counter-Strike 2", "cs2.exe"))


def register(registry: CommandRegistry) -> None:
    registry.add("dota.accept", ["прими катку", "прими игру", "прими доту"], accept_dota)
    registry.add("cs.accept", ["прими катку в кс", "прими кс", "прими контру"], accept_cs)
