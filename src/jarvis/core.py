"""Распознанная фраза -> команда. Здесь нет ничего про Windows, поэтому всё легко тестировать."""

import re
import traceback
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

# Как распознаватель может услышать имя. Если Vosk слышит "Джарвис" по-другому — добавь вариант сюда.
WAKE_WORDS = ("джарвис", "jarvis", "джервис", "жарвис")


def normalize(text: str) -> str:
    """'Джарвис, ПРИМИ катку!' -> 'джарвис прими катку'"""
    text = text.lower().replace("ё", "е")
    return " ".join(re.findall(r"\w+", text))


@dataclass
class Command:
    name: str  # для логов: "dota.accept"
    phrases: list[str]  # уже нормализованные
    action: Callable[[], None]


class CommandRegistry:
    """Список голосовых команд. Модули (игры, музыка, ...) регистрируют сюда свои фразы."""

    def __init__(self) -> None:
        self.commands: list[Command] = []

    def add(self, name: str, phrases: list[str], action: Callable[[], None]) -> None:
        self.commands.append(Command(name, [normalize(p) for p in phrases], action))

    def command(self, name: str, *phrases: str):
        """То же, что add, но декоратором:

        @registry.command("dota.accept", "прими катку")
        def accept(): ...
        """

        def decorator(action: Callable[[], None]) -> Callable[[], None]:
            self.add(name, list(phrases), action)
            return action

        return decorator

    def find(self, text: str) -> Command | None:
        """Ищет команду, фраза которой целиком (по словам) есть в тексте.

        Если подходят несколько — берётся самая длинная фраза,
        чтобы "прими катку в кс" не сработало как просто "прими катку".
        """
        haystack = f" {normalize(text)} "  # пробелы по краям — ищем только целые слова
        best, best_length = None, 0
        for command in self.commands:
            for phrase in command.phrases:
                if len(phrase) > best_length and f" {phrase} " in haystack:
                    best, best_length = command, len(phrase)
        return best


class CommandError(Exception):
    """Команда не получилась. Джарвис произнесёт: "Ошибка. <текст исключения>".

    raise CommandError("не нашёл окно Dota 2")
    """


class HandleResult(Enum):
    IGNORED = auto()  # в фразе не было "Джарвис" — это не нам
    UNKNOWN = auto()  # к нам обратились, но команду не поняли
    EXECUTED = auto()  # команда выполнена
    FAILED = auto()  # команда упала с ошибкой


class Assistant:
    """Ищет в фразе обращение "Джарвис", запускает команду и отвечает голосом, получилось или нет."""

    def __init__(self, registry: CommandRegistry, say: Callable[[str], None] = print) -> None:
        self.registry = registry
        self.say = say  # в программе — speech.say (голосом), в тестах — сбор ответов в список

    def expected_phrases(self) -> list[str]:
        """Всё, что имеет смысл распознавать: "джарвис" и "джарвис <команда>".

        Отдаётся в Vosk как грамматика — с ней маленькая модель не путает "катку" с "кадкой".
        """
        wake = WAKE_WORDS[0]
        return [wake] + [f"{wake} {phrase}" for command in self.registry.commands for phrase in command.phrases]

    def handle(self, heard: str) -> HandleResult:
        words = normalize(heard).split()
        wake_index = next((i for i, word in enumerate(words) if word in WAKE_WORDS), None)
        if wake_index is None:
            return HandleResult.IGNORED

        command = self.registry.find(" ".join(words[wake_index + 1 :]))
        if command is None:
            self.say("Не понял команду")
            return HandleResult.UNKNOWN

        print(f"[jarvis] {command.name}")
        try:
            command.action()
        except CommandError as error:
            self.say(f"Ошибка. {error}")
            return HandleResult.FAILED
        except Exception:
            traceback.print_exc()  # подробности — в консоль, вслух — коротко
            self.say("Ошибка")
            return HandleResult.FAILED

        self.say("Успешно")
        return HandleResult.EXECUTED
