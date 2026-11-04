"""Весь звук Джарвиса: уши (микрофон через Vosk или клавиатура) и рот (ответы голосом).

Голос идёт в устройство вывода по умолчанию.
Windows — встроенный синтез речи SAPI, русский голос "Microsoft Irina" уже есть в системе.
Linux — espeak-ng, ставится отдельно: sudo apt install espeak-ng

(pyttsx3 не подошёл: на Windows он молча пропускает все фразы после первой.)
"""

import json
import queue
import shutil
import subprocess
import sys
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


if sys.platform == "win32":
    _voice = None

    def _speak(text: str) -> None:
        global _voice
        if _voice is None:  # голос создаётся один раз — это занимает заметное время
            import comtypes.client

            _voice = comtypes.client.CreateObject("SAPI.SpVoice")
            voices = _voice.GetVoices()
            russian = next((voices.Item(i) for i in range(voices.Count) if "RU-RU" in voices.Item(i).Id.upper()), None)
            if russian is not None:
                _voice.Voice = russian
            else:
                print("[jarvis] русский голос не найден, говорю голосом по умолчанию")
        _voice.Speak(text)  # ждёт, пока фраза договорится

else:

    def _speak(text: str) -> None:
        if shutil.which("espeak-ng") is None:
            print("[jarvis] нет espeak-ng, говорить не могу: sudo apt install espeak-ng")
            return
        subprocess.run(["espeak-ng", "-v", "ru", text], check=False)


def say(text: str) -> None:
    """Напечатать фразу в консоль и произнести её."""
    print(f"[jarvis] {text}")
    _speak(text)
