"""Открыть сайт в браузере по умолчанию: "Джарвис, открой гугл"."""

import webbrowser

from jarvis.core import CommandError, CommandRegistry

# Сайт: (фразы, адрес). Новый сайт — просто ещё одна строка.
# Фразы — русскими словами: английских "google"/"youtube" модель Vosk не знает.
SITES = {
    "google": (["открой гугл"], "https://www.google.com"),
    "youtube": (["открой ютуб"], "https://www.youtube.com"),
}


def open_site(url: str) -> None:
    if not webbrowser.open_new_tab(url):
        raise CommandError("Не смог открыть браузер")


def register(registry: CommandRegistry) -> None:
    for name, (phrases, url) in SITES.items():
        registry.add(f"web.{name}", phrases, lambda url=url: open_site(url))
