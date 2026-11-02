from jarvis.core import Assistant, CommandError, CommandRegistry, HandleResult, normalize


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
    assert registry.find("прими каткун") is None  # только целые слова
    assert registry.find("включи музыку") is None


def test_command_decorator():
    registry = CommandRegistry()

    @registry.command("music.pause", "пауза")
    def pause():
        pass

    assert registry.find("пауза").action is pause


def test_expected_phrases_for_vosk_grammar():
    registry = CommandRegistry()
    registry.add("dota", ["Прими катку"], lambda: None)
    assert Assistant(registry).expected_phrases() == ["джарвис", "джарвис прими катку"]


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
