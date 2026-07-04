import pytest

from src.i18n import (
    DEFAULT_LOCALE,
    get_locale,
    load_locale,
    save_locale,
    set_locale,
    t,
)


@pytest.fixture(autouse=True)
def restore_locale():
    previous = get_locale()
    set_locale(DEFAULT_LOCALE)
    yield
    set_locale(previous)


def test_t_returns_english_by_default():
    set_locale("en")
    assert t("gui.section.downloads") == "Downloads"


def test_t_returns_spanish_when_locale_is_es():
    set_locale("es")
    assert t("gui.section.downloads") == "Descargas"


def test_t_interpolates_placeholders():
    set_locale("en")
    assert t("gui.rated.data_found", path="/tmp/data") == "Data found in: /tmp/data"


def test_t_falls_back_to_english_for_missing_spanish_key():
    set_locale("es")
    assert t("gui.section.downloads") == "Descargas"


def test_set_locale_rejects_unknown_locale():
    with pytest.raises(ValueError, match="Unsupported locale"):
        set_locale("fr")


def test_save_and_load_locale(tmp_path, monkeypatch):
    config_path = tmp_path / ".childconicity_locale"
    monkeypatch.setattr("src.i18n.locale_config_path", lambda: str(config_path))

    save_locale("es")
    set_locale("en")
    load_locale()

    assert get_locale() == "es"
