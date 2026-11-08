import webbrowser

import pygetwindow
import subprocess #power shell

from src import cursors, paths
from src.core import CommandError, CommandRegistry
from src.system import capture, click, find_window, focused, press_key
from src.vision import find_green_button

DEFAULT_CURSOR_SIZE = 4  # твой размер курсора для команды "моя настройка"

# Как числа звучат голосом: модель отдаёт слова, а не цифры. Место в списке — это размер.
SIZE_WORDS = (
    "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь",
    "девять", "десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать",
)  # fmt: skip


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


def change_cursor_size(size: int) -> None:
    cursors.set_size(size)
    print(f"[jarvis] размер курсора: {size}")


def random_cursor_size() -> None:
    change_cursor_size(cursors.random_size(cursors.current_size()))


# ---------- Моя настройка ----------


def my_settings() -> None:
    change_cursor_size(DEFAULT_CURSOR_SIZE)

    #отлючать дисплей НИКОГДА
    script = "; ".join([
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOIDLE 0",
        "powercfg /setdcvalueindex SCHEME_CURRENT SUB_VIDEO VIDEOIDLE 0",
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0",
        "powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP STANDBYIDLE 0",
        "powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP HIBERNATEIDLE 0",
        "powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP HIBERNATEIDLE 0",
        "powercfg /setactive SCHEME_CURRENT",
    ])
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True, text=True
    )

    # Уберает мусор с рабочего стала
    script2 = (
        "$k='HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\HideDesktopIcons\\NewStartPanel'; "
        "if (!(Test-Path $k)) { New-Item $k -Force | Out-Null }; "
        "Set-ItemProperty $k '{645FF040-5081-101B-9F08-00AA002F954E}' 1 -Type DWord; "  # Корзина
        "Set-ItemProperty $k '{018D5C66-4533-4307-9B53-224DE2ED1FE6}' 1 -Type DWord; "  # OneDrive
        "Set-ItemProperty $k '{2cc5ca98-6485-489a-920e-b3e88a6ccfe3}' 1 -Type DWord; "  # Spotlight
        "$p='HKCU:\\Software\\Policies\\Microsoft\\Windows\\CloudContent'; "
        "if (!(Test-Path $p)) { New-Item $p -Force | Out-Null }; "
        "Set-ItemProperty $p 'DisableSpotlightCollectionOnDesktop' 1 -Type DWord; "
        "Stop-Process -Name explorer -Force"
    )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script2],
        capture_output=True, text=True
    )
    print(result.stderr)
# ---------- Список всех команд ----------


def register_all(registry: CommandRegistry) -> None:
    # Игры
    registry.add("dota.accept", ["прими катку в доте", "прими дотку", "прими доту"], accept_dota)
    registry.add("cs.accept", ["прими катку в кс", "прими кс", "прими контру", "прими каэску"], accept_cs)

    # Сайты
    registry.add("web.google", ["открой гугл", "окрой гугол"], lambda: open_site("https://www.google.com"))
    registry.add("web.youtube", ["открой ютуб", "открой ютубчик"], lambda: open_site("https://www.youtube.com"))

    # Курсоры
    registry.add("cursor.dota", ["поменяй курсор на доту", "поменяй курсор на дота"], lambda: change_cursor("dota"))
    registry.add("cursor.dark", ["поменяй курсор на дарк"], lambda: change_cursor("durck"))
    registry.add("cursor.violet",["поменяй курсор на окси виолет", "поменяй курсор на виолет", "поменяй курсор на фиолетовый"],
        lambda: change_cursor("oxy-violet"),
    )
    registry.add("cursor.small", ["поменяй курсор на маленький"], lambda: change_cursor("small_edition_dark"))
    registry.add("cursor.next", ["поменяй на следующий курсор", "поменяй курсор на следующий"], next_cursor)
    registry.add("cursor.random", ["поменяй на случайный курсор", "поменяй курсор на случайный", "курсор рандомный", "случайный курсор"], random_cursor)

    # Размер курсора
    for size, word in enumerate(SIZE_WORDS, start=1):
        # size=size: без этого все команды поставили бы последний размер из цикла
        registry.add(f"cursor.size.{size}", [f"поменяй размер курсора на {word}"], lambda size=size: change_cursor_size(size))
    registry.add("cursor.size.random", ["поменяй размер курсора на случайный"], random_cursor_size)

    # Моя настройка
    registry.add("settings.mine", ["моя дефолтная настройка", "моя настройка", "мои настройки"], my_settings)
