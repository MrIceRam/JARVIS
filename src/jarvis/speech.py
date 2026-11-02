"""Ответы голосом через устройство вывода звука по умолчанию.

Windows — встроенный синтез речи SAPI, русский голос "Microsoft Irina" уже есть в системе.
Linux — espeak-ng, ставится отдельно: sudo apt install espeak-ng

(pyttsx3 не подошёл: на Windows он молча пропускает все фразы после первой.)
"""

import shutil
import subprocess
import sys

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
