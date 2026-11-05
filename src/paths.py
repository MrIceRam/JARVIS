"""Пути проекта. Всё лежит рядом с исходниками, на диске D: — переживает переустановку Windows."""

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent  # src -> корень репозитория

START_SOUND = PACKAGE_DIR / "assets" / "sounds" / "JARVIS_start.wav"
CURSORS_DIR = PACKAGE_DIR / "assets" / "cursors"

# Модель Vosk качается отдельно: https://alphacephei.com/vosk/models
DEFAULT_MODEL = PROJECT_ROOT / "models" / "vosk-model-small-ru-0.22"

# Куда складывать настройки Windows. Можно переопределить переменной окружения.
DEFAULT_BACKUP_DIR = Path(os.environ.get("JARVIS_BACKUP_DIR", PROJECT_ROOT / "backup"))

# Что видел Джарвис, когда не нашёл кнопку "Принять" в CS2. Каждый раз перезаписывается.
DEBUG_SCREENSHOT = PROJECT_ROOT / "debug" / "cs2_accept.png"

# Автозапуск: uv создаёт jarvis.exe при `uv sync`, ярлык на него лежит в автозагрузке Windows
JARVIS_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "jarvis.exe"
STARTUP_LINK = Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/Startup/Jarvis.lnk"
