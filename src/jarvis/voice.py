"""Источники фраз: микрофон (Vosk, офлайн) или клавиатура для отладки."""

import json
import queue
from collections.abc import Iterator
from pathlib import Path

SAMPLE_RATE = 16000


def listen_console() -> Iterator[str]:
    """Фразы вводятся с клавиатуры. Выход — Ctrl+C."""
    while True:
        try:
            yield input("> ")
        except EOFError:
            return


def listen_microphone(model_path: Path, phrases: list[str]) -> Iterator[str]:
    """Слушает микрофон по умолчанию и отдаёт распознанные фразы.

    Распознаёт только phrases (грамматика Vosk), всё остальное приходит как пустая строка и пропускается.
    """
    # Импорт здесь, чтобы режим --text и тесты не грузили модель и звук
    import sounddevice
    import vosk

    vosk.SetLogLevel(-1)  # без простыни логов Kaldi
    grammar = json.dumps([*phrases, "[unk]"], ensure_ascii=False)
    recognizer = vosk.KaldiRecognizer(vosk.Model(str(model_path)), SAMPLE_RATE, grammar)
    audio: queue.Queue[bytes] = queue.Queue()

    def on_audio(data, frames, time, status) -> None:
        audio.put(bytes(data))

    with sounddevice.RawInputStream(
        samplerate=SAMPLE_RATE, blocksize=8000, dtype="int16", channels=1, callback=on_audio
    ):
        while True:
            if recognizer.AcceptWaveform(audio.get()):
                text = json.loads(recognizer.Result())["text"].replace("[unk]", "").strip()
                if text:
                    yield text
