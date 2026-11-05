import re

from src import commands, cursors
from src.core import CommandRegistry


def registry() -> CommandRegistry:
    result = CommandRegistry()
    commands.register_all(result)
    return result


def test_every_phrase_finds_its_own_command():
    commands_list = registry().commands
    for command in commands_list:
        for phrase in command.phrases:
            assert registry().find(phrase).name == command.name, phrase


def test_phrases_are_not_repeated():
    phrases = [phrase for command in registry().commands for phrase in command.phrases]
    assert len(phrases) == len(set(phrases))


def test_phrases_are_russian_only():
    # Английских слов модель Vosk не знает: такая фраза никогда не распознается
    for command in registry().commands:
        for phrase in command.phrases:
            assert not re.search(r"[a-z]", phrase), phrase


def test_cursor_phrases_pick_the_right_pack(monkeypatch):
    applied = []
    monkeypatch.setattr(cursors, "apply_pack", applied.append)
    monkeypatch.setattr(cursors, "current_pack", lambda: "dota")
    commands_by_phrase = registry()

    for phrase in (
        "поменяй курсор на доту",
        "поменяй курсор на дарк",
        "поменяй курсор на окси виолет",
        "поменяй курсор на маленький",
        "поменяй на следующий курсор",
    ):
        commands_by_phrase.find(phrase).action()

    assert applied == ["dota", "durck", "oxy-violet", "small_edition_dark", "durck"]
