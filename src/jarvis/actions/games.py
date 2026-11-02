"""Принять найденную игру в Dota 2 / CS2. В обеих кнопка "Принять" жмётся Enter'ом."""

from jarvis.core import CommandError, CommandRegistry
from jarvis.system import press_key_in_window


def accept_match(window_title: str) -> None:
    if not press_key_in_window(window_title, "enter"):
        raise CommandError(f"Не нашёл окно {window_title}")


def register(registry: CommandRegistry) -> None:
    registry.add("dota.accept", ["прими катку", "прими игру", "прими доту"], lambda: accept_match("Dota 2"))
    registry.add("cs.accept", ["прими катку в кс", "прими кс", "прими контру"], lambda: accept_match("Counter-Strike 2"))
