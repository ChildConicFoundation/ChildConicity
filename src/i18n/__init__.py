import os

from src.i18n.messages import MESSAGES

DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = ("en", "es")
_LOCALE = DEFAULT_LOCALE


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def locale_config_path():
    return os.path.join(_project_root(), ".childconicity_locale")


def load_locale():
    global _LOCALE

    env_locale = os.environ.get("CHILDCONICITY_LOCALE", "").strip().lower()
    if env_locale in SUPPORTED_LOCALES:
        _LOCALE = env_locale
        return _LOCALE

    config_path = locale_config_path()
    if os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as file:
            stored = file.read().strip().lower()
        if stored in SUPPORTED_LOCALES:
            _LOCALE = stored
            return _LOCALE

    _LOCALE = DEFAULT_LOCALE
    return _LOCALE


def save_locale(locale):
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")

    with open(locale_config_path(), "w", encoding="utf-8") as file:
        file.write(locale)


def get_locale():
    return _LOCALE


def set_locale(locale):
    global _LOCALE
    if locale not in SUPPORTED_LOCALES:
        raise ValueError(f"Unsupported locale: {locale}")
    _LOCALE = locale


def t(key, /, **kwargs):
    catalog = MESSAGES.get(_LOCALE) or MESSAGES[DEFAULT_LOCALE]
    template = catalog.get(key)
    if template is None:
        fallback = MESSAGES[DEFAULT_LOCALE].get(key)
        if fallback is None:
            raise KeyError(key)
        template = fallback

    if kwargs:
        return template.format(**kwargs)
    return template


load_locale()
