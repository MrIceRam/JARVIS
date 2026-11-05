<h1 align="center">JARVIS</h1>

Голосовой помощник для бытовых задач под Windows: принять катку в Dota 2 / CS2 голосом,
сохранить и вернуть настройки (курсор, шрифты, OBS, DaVinci Resolve) после переустановки Windows.

## Установка

Нужен [uv](https://docs.astral.sh/uv/) — он сам поставит Python и все библиотеки:

```
winget install astral-sh.uv
uv sync
```

Для распознавания речи скачай модель `vosk-model-small-ru-0.22` с https://alphacephei.com/vosk/models
и распакуй в `models/` (получится `models/vosk-model-small-ru-0.22/`).

## Использование

```
uv run jarvis                  слушать микрофон: "Джарвис, прими катку"
uv run jarvis --text           то же, но фразы вводятся с клавиатуры
uv run jarvis list             что умеет сохранять
uv run jarvis backup  [имя]    сохранить настройки (без имени — все)
uv run jarvis restore [имя]    вернуть настройки после переустановки
uv run jarvis autostart on     запускать вместе с Windows (off — выключить)
uv run jarvis cursor [имя]     поставить пак курсоров (без имени — показать список)
uv run pytest                  тесты
```

Бэкапы лежат в `backup/` (поменять: `--dir` или переменная `JARVIS_BACKUP_DIR`).
Папка в `.gitignore` — там бывают ключи стрима OBS.

## Структура

```
src/
  cli.py            команды jarvis / list / backup / restore / autostart / cursor
  core.py           Assistant (обращение "Джарвис") и CommandRegistry (фраза -> действие)
  voice.py          микрофон (Vosk), ввод с клавиатуры, ответы голосом
  system.py         окна, клавиши, клики, скриншоты, звук, автозапуск
  vision.py         поиск кнопки на скриншоте
  commands.py       все голосовые команды: игры, сайты, курсоры
  backup.py         сохранение/восстановление настроек Windows
  cursors.py        установка паков курсоров
  assets/           звуки и паки курсоров
tests/              pytest
```

Новая команда — функция и строка `registry.add(...)` в `src/commands.py`.

Джарвис отвечает голосом через устройство вывода по умолчанию: «Успешно», если команда прошла,
и «Ошибка», если нет. Чтобы он сказал причину, функция команды кидает `CommandError`:

```python
from src.core import CommandError

raise CommandError("Не нашёл окно Dota 2")   # Джарвис скажет: "Ошибка. Не нашёл окно Dota 2"
```

На Linux для голоса нужен espeak-ng: `sudo apt install espeak-ng`.

Команды, которые тебе понадобятся
uv sync
Ставит всё по uv.lock. Первая команда после клонирования проекта или переустановки Windows.

uv run jarvis
Запускает программу из .venv, активировать окружение не нужно.

uv add requests
Добавляет библиотеку: обновляет pyproject.toml и uv.lock и сразу ставит её. Удаляется так же: uv remove requests.

uv run pytest
