import webbrowser

import pygetwindow

from src import cursors, paths
from src.core import CommandError, CommandRegistry
from src.system import capture, click, find_window, focused, press_key
from src.vision import find_green_button


# ---------- Игры ----------

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


# ---------- Сайты ----------


def open_site(url: str) -> None:
    if not webbrowser.open_new_tab(url):
        raise CommandError("Не смог открыть браузер")


# ---------- Курсоры ----------


def change_cursor(name: str) -> None:
    cursors.apply_pack(name)
    print(f"[jarvis] курсор: {name}")


def next_cursor() -> None:
    change_cursor(cursors.next_pack(cursors.current_pack()))


def random_cursor() -> None:
    change_cursor(cursors.random_pack(cursors.current_pack()))


# ---------- Список всех команд ----------


def register_all(registry: CommandRegistry) -> None:
    # Игры
    registry.add("dota.accept", ["прими катку", "прими игру", "прими доту"], accept_dota)
    registry.add("cs.accept", ["прими катку в кс", "прими кс", "прими контру"], accept_cs)

    # Сайты
    registry.add("web.google", ["открой гугл"], lambda: open_site("https://www.google.com"))
    registry.add("web.youtube", ["открой ютуб"], lambda: open_site("https://www.youtube.com"))

    # Курсоры
    registry.add("cursor.dota", ["поменяй курсор на доту", "поменяй курсор на дота"], lambda: change_cursor("dota"))
    registry.add("cursor.dark", ["поменяй курсор на дарк"], lambda: change_cursor("durck"))
    registry.add(
        "cursor.violet",
        ["поменяй курсор на окси виолет", "поменяй курсор на виолет", "поменяй курсор на фиолетовый"],
        lambda: change_cursor("oxy-violet"),
    )
    registry.add("cursor.small", ["поменяй курсор на маленький"], lambda: change_cursor("small_edition_dark"))
    registry.add("cursor.next", ["поменяй на следующий курсор", "поменяй курсор на следующий"], next_cursor)
    registry.add("cursor.random", ["поменяй на случайный курсор", "поменяй курсор на случайный"], random_cursor)
