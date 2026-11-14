import pytest

from src.i18n import (
    DEFAULT_LOCALE,
    MESSAGES,
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


def test_load_locale_prefers_the_environment(monkeypatch):
    monkeypatch.setenv("CHILDCONICITY_LOCALE", "es")

    assert load_locale() == "es"
    assert get_locale() == "es"


def test_load_locale_uses_english_when_nothing_is_stored(tmp_path, monkeypatch):
    monkeypatch.delenv("CHILDCONICITY_LOCALE", raising=False)
    monkeypatch.setattr(
        "src.i18n.locale_config_path",
        lambda: str(tmp_path / "missing"),
    )
    set_locale("es")

    assert load_locale() == "en"


def test_load_locale_ignores_an_unknown_stored_value(tmp_path, monkeypatch):
    config_path = tmp_path / ".childconicity_locale"
    config_path.write_text("fr", encoding="utf-8")
    monkeypatch.delenv("CHILDCONICITY_LOCALE", raising=False)
    monkeypatch.setattr("src.i18n.locale_config_path", lambda: str(config_path))
    set_locale("es")

    assert load_locale() == "en"


def test_save_locale_rejects_an_unknown_locale(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.i18n.locale_config_path",
        lambda: str(tmp_path / ".childconicity_locale"),
    )

    with pytest.raises(ValueError, match="Unsupported locale"):
        save_locale("fr")


def test_t_uses_the_english_text_when_spanish_has_no_entry():
    set_locale("es")
    key = "gui.section.downloads"
    removed = MESSAGES["es"].pop(key)
    try:
        assert t(key) == MESSAGES["en"][key]
    finally:
        MESSAGES["es"][key] = removed


def test_t_rejects_an_unknown_key():
    with pytest.raises(KeyError):
        t("gui.missing.key")


def test_save_and_load_locale(tmp_path, monkeypatch):
    config_path = tmp_path / ".childconicity_locale"
    monkeypatch.setattr("src.i18n.locale_config_path", lambda: str(config_path))

    save_locale("es")
    set_locale("en")
    load_locale()

    assert get_locale() == "es"
