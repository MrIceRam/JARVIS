"""Распознанная фраза -> команда. Здесь нет ничего про Windows, поэтому всё легко тестировать."""

import re
import traceback
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum, auto
from typing import Callable

# Как распознаватель может услышать имя. Похожие слова ("жарвис", "дарвис") тоже подходят — см. WAKE_SIMILARITY.
WAKE_WORDS = ("джарвис", "jarvis", "джервис", "жарвис")

# Насколько похожим должно быть услышанное, от 0 до 1. Модель ошибается в отдельных буквах
# ("катков до те" вместо "катку в доте" — 0.89), а посторонние фразы набирают меньше 0.5.
MATCH_SIMILARITY = 0.75
WAKE_SIMILARITY = 0.75


def similarity(a: str, b: str) -> float:
    """Похожесть двух строк: 1.0 — одинаковые, 0 — ничего общего."""
    return SequenceMatcher(None, a, b).ratio()


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
        """Ищет команду, фраза которой больше всего похожа на кусок текста.

        Совпадать буква в букву не обязательно: модель может услышать "катков" вместо "катку".
        Побеждает самая похожая фраза, при равенстве — самая длинная,
        чтобы "прими катку в кс" не сработало как просто "прими кс".
        """
        command, score = self.best_match(text)
        return command if score >= MATCH_SIMILARITY else None

    def best_match(self, text: str) -> tuple[Command | None, float]:
        """Самая похожая команда и её оценка, даже если она ниже порога (для отладки)."""
        words = normalize(text).split()
        best, best_score, best_length = None, 0.0, 0
        for command in self.commands:
            for phrase in command.phrases:
                score = _phrase_similarity(words, phrase)
                if (score, len(phrase)) > (best_score, best_length):
                    best, best_score, best_length = command, score, len(phrase)
        return best, best_score


def _phrase_similarity(words: list[str], phrase: str) -> float:
    """Сравнивает фразу с каждым куском текста примерно той же длины и берёт лучший.

    Длина куска плюс-минус одно слово: модель иногда склеивает или разрывает слова
    ("доте" -> "до те").
    """
    length = len(phrase.split())
    best = 0.0
    for size in (length - 1, length, length + 1):
        if size < 1:
            continue
        for start in range(max(1, len(words) - size + 1)):
            best = max(best, similarity(" ".join(words[start : start + size]), phrase))
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
        self.say = say  # в программе — voice.say (голосом), в тестах — сбор ответов в список

    def handle(self, heard: str) -> HandleResult:
        words = normalize(heard).split()
        wake_index = next((i for i, word in enumerate(words) if _is_wake_word(word)), None)
        if wake_index is None:
            return HandleResult.IGNORED

        command, score = self.registry.best_match(" ".join(words[wake_index + 1 :]))
        if command is None or score < MATCH_SIMILARITY:
            if command is not None:
                print(f"[jarvis] ближе всего {command.name}, но похожесть {score:.2f} — мало")
            self.say("Не понял команду")
            return HandleResult.UNKNOWN

        print(f"[jarvis] {command.name} (похожесть {score:.2f})")
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


def _is_wake_word(word: str) -> bool:
    return any(similarity(word, wake) >= WAKE_SIMILARITY for wake in WAKE_WORDS)
