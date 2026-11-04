from src.system import autostart_enabled, disable_autostart, enable_autostart


def test_enable_and_disable(tmp_path):
    link = tmp_path / "Jarvis.lnk"  # настоящая автозагрузка в тестах не трогается
    assert not autostart_enabled(link)

    enable_autostart(link)
    assert autostart_enabled(link)

    disable_autostart(link)
    assert not autostart_enabled(link)
    disable_autostart(link)  # повторное выключение не падает
