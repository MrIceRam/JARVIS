from jarvis import autostart


def test_enable_and_disable(tmp_path):
    link = tmp_path / "Jarvis.lnk"  # настоящая автозагрузка в тестах не трогается
    assert not autostart.is_enabled(link)

    autostart.enable(link)
    assert autostart.is_enabled(link)

    autostart.disable(link)
    assert not autostart.is_enabled(link)
    autostart.disable(link)  # повторное выключение не падает
