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
import tempfile
import urllib.request
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path

from src import paths

SAMPLE_RATE = 16000


def _show_progress(blocks: int, block_size: int, total: int) -> None:
    if total > 0:
        percent = min(100, blocks * block_size * 100 // total)
        print(f"\r  скачано {percent}%", end="", flush=True)


def download_model(target: Path = paths.DEFAULT_MODEL, url: str = paths.MODEL_URL) -> None:
    """Скачать и распаковать модель Vosk.

    Всё делается во временной папке, а на место модель встаёт одним переименованием:
    оборванная загрузка не оставит наполовину распакованную модель.
    Тяжёлые необязательные части (paths.MODEL_SKIP) выбрасываются, чтобы модель грузилась быстро.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as folder:
        archive = Path(folder) / "model.zip"
        urllib.request.urlretrieve(url, archive, reporthook=_show_progress)
        print()
        with zipfile.ZipFile(archive) as model_zip:
            model_zip.extractall(folder)
        unpacked = Path(folder) / target.name
        for part in paths.MODEL_SKIP:
            shutil.rmtree(unpacked / part, ignore_errors=True)
        unpacked.rename(target)


def listen_console() -> Iterator[str]:
    """Фразы вводятся с клавиатуры. Выход — Ctrl+C."""
    while True:
        try:
            yield input("> ")
        except EOFError:
            return


def listen_microphone(model_path: Path, on_ready: Callable[[], None] | None = None) -> Iterator[str]:
    """Слушает микрофон по умолчанию и отдаёт распознанные фразы.

    Распознаёт любую речь, а не только команды: что услышано, то и отдаётся.
    Какая это команда, решает уже core.py, и сравнивает он нечётко.
    on_ready вызывается, когда модель загрузилась и микрофон включён — до этого Джарвис глухой.
    """
    # Импорт здесь, чтобы режим --text и тесты не грузили модель и звук
    import sounddevice
    import vosk

    vosk.SetLogLevel(-1)  # без простыни логов Kaldi
    print("Загружаю модель распознавания...")
    recognizer = vosk.KaldiRecognizer(vosk.Model(str(model_path)), SAMPLE_RATE)
    audio: queue.Queue[bytes] = queue.Queue()

    def on_audio(data, frames, time, status) -> None:
        audio.put(bytes(data))

    with sounddevice.RawInputStream(
        samplerate=SAMPLE_RATE, blocksize=8000, dtype="int16", channels=1, callback=on_audio
    ):
        if on_ready:
            on_ready()
        while True:
            if recognizer.AcceptWaveform(audio.get()):
                text = json.loads(recognizer.Result())["text"].strip()
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
