"""Точка входа: `uv run jarvis ...`"""

import argparse
from pathlib import Path

from src import backup, paths


def run_assistant(text_mode: bool, model: Path) -> int:
    from src import commands, voice
    from src.core import Assistant, CommandRegistry
    from src.system import already_running, play_sound

    registry = CommandRegistry()
    commands.register_all(registry)
    assistant = Assistant(registry, say=voice.say)

    def ready() -> None:
        """Звук запуска — только когда Джарвис правда готов слушать."""
        play_sound(paths.START_SOUND)
        print("Привет, я Джарвис. Слушаю. Выход — Ctrl+C.")

    if text_mode:
        phrases = voice.listen_console()
        ready()
    elif already_running():
        # Два Джарвиса на одном микрофоне выполняли бы каждую команду дважды
        print("Джарвис уже запущен: его окно свёрнуто на панели задач.")
        return 1
    elif model.exists():
        phrases = voice.listen_microphone(model, on_ready=ready)
    else:
        print(f"Нет модели Vosk: {model}")
        print("Скачай её командой: uv run jarvis setup")
        print("Или запусти с --text, чтобы вводить фразы с клавиатуры.")
        return 1

    for heard in phrases:
        if not text_mode:
            print(f"[слышу] {heard}")
        assistant.handle(heard)  # ответ "Успешно" / "Ошибка" Джарвис произносит сам
    return 0


def run_backup(mode: str, only: str | None, storage: Path) -> int:
    targets = [t for t in backup.TARGETS if only in (None, t.name)]
    if not targets:
        print(f"Нет такой цели: {only} (см. jarvis list)")
        return 1

    print(f"Папка бэкапов: {storage}")
    if mode == "restore":
        print("Закрой OBS и DaVinci Resolve перед восстановлением.")
    for target in targets:
        (backup.backup if mode == "backup" else backup.restore)(target, storage)
    return 0


def run_autostart(state: str | None) -> int:
    from src.system import autostart_enabled, disable_autostart, enable_autostart

    if state == "on":
        if not paths.JARVIS_EXE.exists():
            print(f"Нет {paths.JARVIS_EXE}. Сначала выполни: uv sync")
            return 1
        enable_autostart()
    elif state == "off":
        disable_autostart()

    print(f"Автозапуск {'включён' if autostart_enabled() else 'выключен'}")
    return 0


def run_cursor(name: str | None) -> int:
    from src import cursors

    if name is None:
        print("Паки курсоров:")
        for pack in cursors.PACKS:
            print(f"  {pack}")
        print("Поставить: jarvis cursor <имя>")
        return 0
    if name not in cursors.PACKS:
        print(f"Нет такого пака: {name} (см. jarvis cursor)")
        return 1

    cursors.apply_pack(name)
    print(f"Курсор {name} поставлен")
    return 0


def run_setup(model: Path) -> int:
    import zipfile

    from src import voice

    if model.exists():
        print(f"Модель уже на месте: {model}")
        return 0

    print("Скачиваю модель Vosk: 1,8 ГБ, на диске останется около 1,4 ГБ. Это несколько минут...")
    try:
        voice.download_model(model)
    except (OSError, zipfile.BadZipFile) as error:
        print(f"\nНе удалось скачать модель: {error}")
        print("Проверь интернет и запусти команду ещё раз.")
        return 1
    print(f"Готово: {model}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jarvis", description="Голосовой помощник. Без команды — слушает микрофон.")
    parser.add_argument("--text", action="store_true", help="вводить фразы с клавиатуры вместо микрофона")
    parser.add_argument("--model", type=Path, default=paths.DEFAULT_MODEL, help="папка с моделью Vosk")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("list", help="что умеет сохранять backup/restore")
    for name, help_text in (("backup", "сохранить настройки"), ("restore", "вернуть настройки после переустановки")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("target", nargs="?", help="cursor / fonts / obs / davinci (без имени — все)")
        p.add_argument("--dir", type=Path, default=paths.DEFAULT_BACKUP_DIR, help="папка бэкапов")
    p = sub.add_parser("autostart", help="запуск вместе с Windows")
    p.add_argument("state", nargs="?", choices=["on", "off"], help="включить / выключить (без слова — показать)")
    p = sub.add_parser("cursor", help="поставить пак курсоров из проекта")
    p.add_argument("name", nargs="?", help="имя пака (без имени — показать список)")
    sub.add_parser("setup", help="скачать модель распознавания речи")

    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            for target in backup.TARGETS:
                print(f"  {target.name:8} {target.description}")
            return 0
        if args.command in ("backup", "restore"):
            return run_backup(args.command, args.target, args.dir)
        if args.command == "autostart":
            return run_autostart(args.state)
        if args.command == "cursor":
            return run_cursor(args.name)
        if args.command == "setup":
            return run_setup(args.model)
        return run_assistant(args.text, args.model)
    except KeyboardInterrupt:
        return 0
