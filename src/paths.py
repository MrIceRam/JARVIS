"""Пути проекта. Всё лежит рядом с исходниками, на диске D: — переживает переустановку Windows."""

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent  # src -> корень репозитория

START_SOUND = PACKAGE_DIR / "assets" / "sounds" / "JARVIS_start.wav"
CURSORS_DIR = PACKAGE_DIR / "assets" / "cursors"

# Модель Vosk в git не лежит, её скачивает команда `jarvis setup`.
# Большая модель: точно слышит речь, грузится за несколько секунд, занимает ~1 ГБ памяти.
DEFAULT_MODEL = PROJECT_ROOT / "models" / "vosk-model-ru-0.42"
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip"
# Необязательные части модели для дополнительной проверки результата. С ними загрузка шла 2 минуты
# и 5 ГБ памяти, без них — 3 секунды и 1 ГБ, а команды распознаются так же. setup их не ставит.
MODEL_SKIP = ("rescore", "rnnlm")

# Куда складывать настройки Windows. Можно переопределить переменной окружения.
DEFAULT_BACKUP_DIR = Path(os.environ.get("JARVIS_BACKUP_DIR", PROJECT_ROOT / "backup"))

# Что видел Джарвис, когда не нашёл кнопку "Принять" в CS2. Каждый раз перезаписывается.
DEBUG_SCREENSHOT = PROJECT_ROOT / "debug" / "cs2_accept.png"

# Автозапуск: uv создаёт jarvis.exe при `uv sync`, ярлык на него лежит в автозагрузке Windows
JARVIS_EXE = PROJECT_ROOT / ".venv" / "Scripts" / "jarvis.exe"
STARTUP_LINK = Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/Startup/Jarvis.lnk"
