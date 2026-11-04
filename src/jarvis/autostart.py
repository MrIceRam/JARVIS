"""Запуск Джарвиса вместе с Windows: ярлык в папке автозагрузки."""

from pathlib import Path

from jarvis import paths

MINIMIZED = 7  # окно консоли открывается свёрнутым на панель задач


def is_enabled(link: Path = paths.STARTUP_LINK) -> bool:
    return link.exists()


def enable(link: Path = paths.STARTUP_LINK) -> None:
    import comtypes.client

    shell = comtypes.client.CreateObject("WScript.Shell", dynamic=True)
    shortcut = shell.CreateShortcut(str(link))
    shortcut.TargetPath = str(paths.JARVIS_EXE)
    shortcut.WorkingDirectory = str(paths.PROJECT_ROOT)
    shortcut.WindowStyle = MINIMIZED
    shortcut.Description = "Голосовой помощник Джарвис"
    shortcut.Save()


def disable(link: Path = paths.STARTUP_LINK) -> None:
    link.unlink(missing_ok=True)
