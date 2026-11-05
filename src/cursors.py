"""Паки курсоров, которые лежат в проекте: на любом ПК git clone, uv sync и `jarvis cursor <имя>`.

Новый пак: папка с файлами в src/assets/cursors/ и строка в PACKS.
"""

import ctypes
import random
import winreg

from src import paths

CURSORS_KEY = r"Control Panel\Cursors"

# Роли курсоров в том порядке, в каком Windows хранит их в схеме
ROLES = (
    "Arrow", "Help", "AppStarting", "Wait", "Crosshair", "IBeam", "NWPen", "No", "SizeNS",
    "SizeWE", "SizeNWSE", "SizeNESW", "SizeAll", "UpArrow", "Hand", "Pin", "Person",
)  # fmt: skip

# Пак: {роль: файл}. Роли, которых нет в паке, получают стандартный курсор Windows.
PACKS = {
    "durck": {
        "Arrow": "pointer.cur",
        "Help": "help.cur",
        "AppStarting": "working.ani",
        "Wait": "working.ani",  # как в твоей схеме IceR, хотя в паке есть и busy.ani
        "Crosshair": "precision.cur",
        "IBeam": "beam.cur",
        "NWPen": "handwriting.cur",
        "No": "unavailable.cur",
        "SizeNS": "vert.cur",
        "SizeWE": "horz.cur",
        "SizeNWSE": "dgn1.cur",
        "SizeNESW": "dgn2.cur",
        "SizeAll": "move.cur",
        "UpArrow": "alternate.cur",
        "Hand": "link.cur",
        "Pin": "pin.cur",
        "Person": "person.cur",
    },
    "oxy-violet": {
        "Arrow": "left_ptr.cur",
        "Help": "help.cur",
        "AppStarting": "left_ptr_watch.ani",
        "Wait": "watch.ani",
        "Crosshair": "cross.cur",
        "IBeam": "Text.cur",
        "NWPen": "pencil.cur",
        "No": "forbidden.cur",
        "SizeNS": "size_ver.cur",
        "SizeWE": "size_hor.cur",
        "SizeNWSE": "size_fdiag.cur",
        "SizeNESW": "size_bdiag.cur",
        "SizeAll": "size_all.cur",
        "UpArrow": "up_arrow.cur",
        "Hand": "pointing_hand.cur",
    },
    "small_edition_dark": {
        "Arrow": "pointer.cur",
        "Help": "help.cur",
        "AppStarting": "work.ani",
        "Wait": "busy.ani",
        "Crosshair": "cross.cur",
        "IBeam": "text.cur",
        "NWPen": "handwriting.cur",
        "No": "unavailiable.cur",
        "SizeNS": "vert.cur",
        "SizeWE": "horz.cur",
        "SizeNWSE": "dgn1.cur",
        "SizeNESW": "dgn2.cur",
        "SizeAll": "move.cur",
        "UpArrow": "alternate.cur",
        "Hand": "link.cur",
        "Pin": "link-place.cur",
        "Person": "link-acount.cur",
    },
    "dota": {"Arrow": "Dota1.cur"},  # в паке только стрелка
}


def role_paths(name: str) -> dict[str, str]:
    """Полный путь к файлу для каждой роли. Пустая строка значит стандартный курсор Windows."""
    pack = PACKS[name]
    folder = paths.CURSORS_DIR / name
    return {role: str(folder / pack[role]) if role in pack else "" for role in ROLES}


def current_pack() -> str | None:
    """Какой пак сейчас стоит. None, если стоит что-то не из PACKS."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY) as key:
        scheme = winreg.QueryValueEx(key, "")[0]
    if scheme == "IceR":  # старая схема, собранная вручную: выглядит как durck
        return "durck"
    return scheme if scheme in PACKS else None


def next_pack(current: str | None) -> str:
    """Следующий пак по кругу. Если текущий неизвестен — первый."""
    names = list(PACKS)
    if current not in names:
        return names[0]
    return names[(names.index(current) + 1) % len(names)]


def random_pack(current: str | None) -> str:
    """Случайный пак, но не тот, что стоит сейчас: иначе команда выглядела бы как сломанная."""
    return random.choice([name for name in PACKS if name != current])


def reload_cursors() -> None:
    """Попросить Windows перечитать курсоры из реестра, чтобы они сменились без перезагрузки."""
    SPI_SETCURSORS, SPIF_SENDCHANGE = 0x57, 0x02
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)


def apply_pack(name: str) -> None:
    """Поставить пак текущим и добавить его в список схем в настройках мыши.

    Windows будет брать файлы прямо из папки проекта, поэтому после переноса проекта
    команду надо выполнить ещё раз.
    """
    files = role_paths(name)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, name)
        winreg.SetValueEx(key, "Scheme Source", 0, winreg.REG_DWORD, 1)  # 1 = схема пользователя
        for role, path in files.items():
            winreg.SetValueEx(key, role, 0, winreg.REG_EXPAND_SZ, path)

    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CURSORS_KEY + r"\Schemes") as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, ",".join(files.values()))

    reload_cursors()
