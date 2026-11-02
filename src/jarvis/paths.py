"""Пути проекта. Всё лежит рядом с исходниками, на диске D: — переживает переустановку Windows."""

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parents[1]  # src/jarvis -> корень репозитория

START_SOUND = PACKAGE_DIR / "assets" / "sounds" / "JARVIS_start.wav"

# Модель Vosk качается отдельно: https://alphacephei.com/vosk/models
DEFAULT_MODEL = PROJECT_ROOT / "models" / "vosk-model-small-ru-0.22"

# Куда складывать настройки Windows. Можно переопределить переменной окружения.
DEFAULT_BACKUP_DIR = Path(os.environ.get("JARVIS_BACKUP_DIR", PROJECT_ROOT / "backup"))
