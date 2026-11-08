from src.core import Assistant, CommandError, CommandRegistry, HandleResult, normalize


def test_normalize():
    assert normalize("Джарвис, ПРИМИ катку!") == "джарвис прими катку"
    assert normalize("  ещё   раз  ") == "еще раз"
    assert normalize("") == ""


def test_registry_picks_longest_phrase():
    registry = CommandRegistry()
    registry.add("dota", ["прими катку"], lambda: None)
    registry.add("cs", ["прими катку в кс"], lambda: None)

    assert registry.find("прими катку").name == "dota"
    assert registry.find("Прими катку в КС").name == "cs"
    assert registry.find("включи музыку") is None


def test_registry_forgives_misheard_words():
    # Настоящие ошибки модели Vosk на этих фразах
    registry = CommandRegistry()
    registry.add("dota", ["прими катку в доте"], lambda: None)
    registry.add("cs", ["прими катку в кс"], lambda: None)
    registry.add("mine", ["моя дефолтная настройка"], lambda: None)

    assert registry.find("прими катков до те").name == "dota"
    assert registry.find("прими катков каэс").name == "cs"
    assert registry.find("моя дефолтных настройка").name == "mine"
    assert registry.find("какая сегодня погода в москве") is None


def test_close_commands_are_not_mixed_up():
    registry = CommandRegistry()
    registry.add("two", ["поменяй размер курсора на два"], lambda: None)
    registry.add("three", ["поменяй размер курсора на три"], lambda: None)

    assert registry.find("поменяй размер курсора на два").name == "two"
    assert registry.find("поменяй размер курсора на три").name == "three"


def test_command_decorator():
    registry = CommandRegistry()

    @registry.command("music.pause", "пауза")
    def pause():
        pass

    assert registry.find("пауза").action is pause


def test_wake_word_can_be_misheard():
    calls = []
    registry = CommandRegistry()
    registry.add("dota", ["прими катку"], lambda: calls.append(1))
    assistant = Assistant(registry)

    assert assistant.handle("дарвис прими катку") is HandleResult.EXECUTED
    assert assistant.handle("давай прими катку") is HandleResult.IGNORED  # "давай" на имя не похоже
    assert len(calls) == 1


def test_assistant_needs_wake_word():
    calls = []
    registry = CommandRegistry()
    registry.add("dota", ["прими катку"], lambda: calls.append(1))
    assistant = Assistant(registry)

    assert assistant.handle("прими катку") is HandleResult.IGNORED
    assert assistant.handle("Джарвис, сделай кофе") is HandleResult.UNKNOWN
    assert assistant.handle("Джарвис") is HandleResult.UNKNOWN
    assert assistant.handle("Джарвис, прими катку") is HandleResult.EXECUTED
    assert assistant.handle("эй jarvis прими катку") is HandleResult.EXECUTED
    assert len(calls) == 2


def test_assistant_answers_out_loud():
    def fail_with_reason():
        raise CommandError("Не нашёл окно Dota 2")

    def crash():
        raise RuntimeError("что-то сломалось")

    registry = CommandRegistry()
    registry.add("ok", ["открой гугл"], lambda: None)
    registry.add("fail", ["прими катку"], fail_with_reason)
    registry.add("crash", ["сломайся"], crash)
    answers = []
    assistant = Assistant(registry, say=answers.append)

    assert assistant.handle("джарвис открой гугл") is HandleResult.EXECUTED
    assert assistant.handle("джарвис прими катку") is HandleResult.FAILED
    assert assistant.handle("джарвис сломайся") is HandleResult.FAILED
    assert assistant.handle("джарвис сделай кофе") is HandleResult.UNKNOWN
    assert assistant.handle("просто разговор") is HandleResult.IGNORED  # молчит
    assert answers == ["Успешно", "Ошибка. Не нашёл окно Dota 2", "Ошибка", "Не понял команду"]
