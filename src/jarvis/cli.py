"""Точка входа: `uv run jarvis ...`"""

import argparse
from pathlib import Path

from jarvis import autostart, backup, paths


def run_assistant(text_mode: bool, model: Path) -> int:
    from jarvis import actions, speech, voice
    from jarvis.core import Assistant, CommandRegistry
    from jarvis.system import already_running, play_sound

    registry = CommandRegistry()
    actions.register_all(registry)
    assistant = Assistant(registry, say=speech.say)

    if text_mode:
        phrases = voice.listen_console()
    elif already_running():
        # Два Джарвиса на одном микрофоне выполняли бы каждую команду дважды
        print("Джарвис уже запущен: его окно свёрнуто на панели задач.")
        return 1
    elif model.exists():
        phrases = voice.listen_microphone(model, assistant.expected_phrases())
    else:
        print(f"Нет модели Vosk: {model}")
        print("Скачай vosk-model-small-ru-0.22 с https://alphacephei.com/vosk/models и распакуй в models/")
        print("Или запусти с --text, чтобы вводить фразы с клавиатуры.")
        return 1

    play_sound(paths.START_SOUND)
    print("Привет, я Джарвис. Выход — Ctrl+C.")
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
    if state == "on":
        if not paths.JARVIS_EXE.exists():
            print(f"Нет {paths.JARVIS_EXE}. Сначала выполни: uv sync")
            return 1
        autostart.enable()
    elif state == "off":
        autostart.disable()

    print(f"Автозапуск {'включён' if autostart.is_enabled() else 'выключен'}")
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
        return run_assistant(args.text, args.model)
    except KeyboardInterrupt:
        return 0
