"""Сохранение и восстановление настроек Windows между переустановками.

В бэкапе у каждой цели своя папка:
    backup/obs/files/basic, backup/obs/files/global.ini, ...
    backup/cursor/registry/HKCU_Control_Panel_Cursors.reg
"""

import ctypes
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


def _apply_cursor() -> None:
    SPI_SETCURSORS, SPIF_SENDCHANGE = 0x57, 0x02
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)


def _notify_fonts_changed() -> None:
    HWND_BROADCAST, WM_FONTCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x001D, 0x0002
    ctypes.windll.user32.SendMessageTimeoutW(HWND_BROADCAST, WM_FONTCHANGE, 0, 0, SMTO_ABORTIFHUNG, 1000, None)


@dataclass
class BackupTarget:
    name: str
    description: str
    # Файлы и папки (можно с %APPDATA% и т.п.). В бэкапе лежат под своим именем,
    # поэтому имена в пределах одной цели не должны совпадать.
    paths: list[str] = field(default_factory=list)
    registry_keys: list[str] = field(default_factory=list)
    # Что сделать после восстановления (например, применить курсор без перезагрузки)
    after_restore: Callable[[], None] | None = None


TARGETS = [
    BackupTarget(
        "cursor",
        "Схема курсора мыши",
        # TODO: копировать и сами файлы .cur/.ani, если схема лежит не в C:\Windows\Cursors
        registry_keys=[r"HKCU\Control Panel\Cursors"],
        after_restore=_apply_cursor,
    ),
    BackupTarget(
        "fonts",
        "Шрифты, установленные для пользователя",
        paths=[r"%LOCALAPPDATA%\Microsoft\Windows\Fonts"],
        registry_keys=[r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts"],
        after_restore=_notify_fonts_changed,
    ),
    BackupTarget(
        "obs",
        "OBS: сцены, профили, настройки (без кэша браузера и логов)",
        paths=[
            r"%APPDATA%\obs-studio\basic",
            r"%APPDATA%\obs-studio\global.ini",
            r"%APPDATA%\obs-studio\user.ini",
            r"%APPDATA%\obs-studio\plugin_config\obs-websocket",
        ],
    ),
    BackupTarget(
        "davinci",
        "DaVinci Resolve: настройки, горячие клавиши, Fusion-макросы",
        paths=[
            r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Preferences",
            r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion",
        ],
    ),
]


def _copy(source: Path, destination: Path) -> None:
    if not source.exists():
        print(f"  пропуск, нет такого пути: {source}")  # программа может быть просто не установлена
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source, destination)
    print(f"  {source} -> {destination}")


def _reg_file(key: str) -> str:
    """'HKCU\\Control Panel\\Cursors' -> 'HKCU_Control_Panel_Cursors.reg'"""
    return key.replace("\\", "_").replace(" ", "_") + ".reg"


def _reg(*args: str) -> None:
    subprocess.run(["reg", *args], check=True, stdout=subprocess.DEVNULL)


def backup(target: BackupTarget, storage: Path) -> None:
    print(f"[backup] {target.name}")
    root = storage / target.name
    for path in target.paths:
        source = Path(os.path.expandvars(path))
        _copy(source, root / "files" / source.name)

    for key in target.registry_keys:
        file = root / "registry" / _reg_file(key)
        file.parent.mkdir(parents=True, exist_ok=True)
        _reg("export", key, str(file), "/y")
        print(f"  {key} -> {file}")


def restore(target: BackupTarget, storage: Path) -> None:
    print(f"[restore] {target.name}")
    root = storage / target.name
    if not root.exists():
        print(f"  бэкапа нет: {root}")
        return

    for path in target.paths:
        destination = Path(os.path.expandvars(path))
        _copy(root / "files" / destination.name, destination)

    for key in target.registry_keys:
        file = root / "registry" / _reg_file(key)
        if file.exists():
            _reg("import", str(file))
            print(f"  {file} -> {key}")

    if target.after_restore:
        target.after_restore()
