import zipfile

from src import cli, voice


def fake_model_zip(tmp_path, name="model-x"):
    """Маленький архив вместо настоящей модели, с той же структурой: одна папка внутри."""
    archive = tmp_path / "fake.zip"
    with zipfile.ZipFile(archive, "w") as model_zip:
        model_zip.writestr(f"{name}/README", "модель")
        model_zip.writestr(f"{name}/rescore/G.carpa", "тяжёлое")
        model_zip.writestr(f"{name}/rnnlm/final.raw", "тяжёлое")
    return archive


def test_download_unpacks_model_and_leaves_no_temp_files(tmp_path):
    target = tmp_path / "models" / "model-x"

    voice.download_model(target, fake_model_zip(tmp_path).as_uri())

    assert (target / "README").read_text(encoding="utf-8") == "модель"
    assert [path.name for path in target.parent.iterdir()] == ["model-x"]


def test_download_skips_heavy_optional_parts(tmp_path):
    target = tmp_path / "models" / "model-x"

    voice.download_model(target, fake_model_zip(tmp_path).as_uri())

    assert not (target / "rescore").exists()
    assert not (target / "rnnlm").exists()


def test_broken_download_leaves_no_model(tmp_path, capsys):
    target = tmp_path / "models" / "model-x"
    broken = tmp_path / "broken.zip"
    broken.write_text("это не архив", encoding="utf-8")
    original = voice.download_model

    def download(model):
        original(model, broken.as_uri())

    voice.download_model = download
    try:
        assert cli.run_setup(target) == 1
    finally:
        voice.download_model = original

    assert not target.exists()
    assert "Не удалось скачать" in capsys.readouterr().out


def test_setup_does_nothing_when_model_exists(tmp_path, capsys):
    assert cli.run_setup(tmp_path) == 0
    assert "уже на месте" in capsys.readouterr().out
