"""Действия, которые умеет Джарвис. Каждый модуль добавляет свои команды через register()."""

from jarvis.actions import games, web
from jarvis.core import CommandRegistry


def register_all(registry: CommandRegistry) -> None:
    games.register(registry)
    web.register(registry)
