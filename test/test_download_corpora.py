import io
import zipfile

import pytest
from selenium.common.exceptions import StaleElementReferenceException

from src.cli.download_corpora import (
    BASE_URL,
    INDEX_URL,
    PHON_INDEX_URL,
    TALKBANK_PASSWORD_ENV,
    TALKBANK_USER_ENV,
    _build_chrome,
    _corpus_names_from_index,
    _download_stream,
    _zip_links_from_page,
    download_corpus,
    fetch_corpus_names,
    fetch_download_url,
    login_and_get_cookies,
    main,
    resolve_talkbank_credentials,
    run,
)


def test_resolve_talkbank_credentials_uses_cli_args():
    email, password = resolve_talkbank_credentials(
        user="cli@example.com",
        password="cli-secret",
    )

    assert email == "cli@example.com"
    assert password == "cli-secret"


def test_resolve_talkbank_credentials_uses_environment(monkeypatch):
    monkeypatch.setenv(TALKBANK_USER_ENV, "env@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "env-secret")

    email, password = resolve_talkbank_credentials()

    assert email == "env@example.com"
    assert password == "env-secret"


def test_resolve_talkbank_credentials_prefers_cli_over_environment(monkeypatch):
    monkeypatch.setenv(TALKBANK_USER_ENV, "env@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "env-secret")

    email, password = resolve_talkbank_credentials(
        user="cli@example.com",
        password="cli-secret",
    )

    assert email == "cli@example.com"
    assert password == "cli-secret"


def test_resolve_talkbank_credentials_requires_user_and_password():
    with pytest.raises(ValueError, match=TALKBANK_USER_ENV):
        resolve_talkbank_credentials(password="only-password")

    with pytest.raises(ValueError, match=TALKBANK_PASSWORD_ENV):
        resolve_talkbank_credentials(user="only@example.com")


def test_main_reads_credentials_from_environment(monkeypatch):
    monkeypatch.setenv(TALKBANK_USER_ENV, "env@example.com")
    monkeypatch.setenv(TALKBANK_PASSWORD_ENV, "env-secret")

    calls = []

    def fake_run(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr("src.cli.download_corpora.run", fake_run)

    main(["--corpora", "Brent"])

    assert calls == [
        {
            "email": "env@example.com",
            "password": "env-secret",
            "corpora_filter": ["Brent"],
            "output_dir": "Corpora",
            "force": False,
            "headless": True,
        }
    ]


def test_main_reports_missing_credentials(monkeypatch, capsys):
    monkeypatch.delenv(TALKBANK_USER_ENV, raising=False)
    monkeypatch.delenv(TALKBANK_PASSWORD_ENV, raising=False)

    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert TALKBANK_USER_ENV in captured.err
    assert TALKBANK_PASSWORD_ENV in captured.err


class _Options:
    def __init__(self):
        self.arguments = []

    def add_argument(self, argument):
        self.arguments.append(argument)


class _Chrome:
    def __init__(self, options):
        self.options = options


def test_build_chrome_adds_headless_only_when_requested(monkeypatch):
    monkeypatch.setattr("src.cli.download_corpora.Options", _Options)
    monkeypatch.setattr("src.cli.download_corpora.webdriver.Chrome", _Chrome)

    headless = _build_chrome(headless=True)
    visible = _build_chrome(headless=False)

    assert "--headless=new" in headless.options.arguments
    assert "--headless=new" not in visible.options.arguments
    assert "--no-sandbox" in visible.options.arguments


class _Field:
    def __init__(self, stale=False, text="", stale_after=None):
        self._stale = stale
        self._stale_after = stale_after
        self._reads = 0
        self.text = text
        self.clicked = False
        self.cleared = False
        self.keys = ""

    def click(self):
        self.clicked = True

    def clear(self):
        self.cleared = True

    def send_keys(self, value):
        self.keys += value

    @property
    def tag_name(self):
        self._reads += 1
        if self._stale or (
            self._stale_after is not None and self._reads >= self._stale_after
        ):
            raise StaleElementReferenceException("reloaded")
        return "html"


class _Driver:
    def __init__(self, error_text="", stale=True):
        self.error_text = error_text
        self.sentinel = _Field(stale=stale, stale_after=None if stale else 2)
        self.quit_called = False
        self.url = None

    def get(self, url):
        self.url = url

    def find_element(self, by, value):
        if value == "html":
            return self.sentinel
        return _Field()

    def find_elements(self, by, selector):
        if selector == ".authModals_messageFail" and self.error_text:
            return [_Field(text=self.error_text)]
        return []

    def execute_script(self, script):
        return "complete"

    def get_cookies(self):
        return [{"name": "session", "value": "abc"}]

    def quit(self):
        self.quit_called = True


class _Wait:
    def __init__(self, driver, timeout):
        self.driver = driver

    def until(self, method):
        module = getattr(method, "__module__", None) or type(method).__module__
        if str(module).startswith("selenium"):
            return _Field()
        value = method(self.driver)
        if value is False:
            value = method(self.driver)
        return value


def test_login_and_get_cookies_returns_the_session_cookie(monkeypatch):
    driver = _Driver(stale=False)
    monkeypatch.setattr("src.cli.download_corpora._build_chrome", lambda headless: driver)
    monkeypatch.setattr("src.cli.download_corpora.WebDriverWait", _Wait)

    cookies = login_and_get_cookies("user@example.com", "secret")

    assert cookies == {"session": "abc"}
    assert driver.url.endswith("Brent.html")
    assert driver.quit_called


def test_login_and_get_cookies_turns_an_auth_message_into_permission_error(monkeypatch):
    driver = _Driver(error_text="Invalid password")
    monkeypatch.setattr("src.cli.download_corpora._build_chrome", lambda headless: driver)
    monkeypatch.setattr("src.cli.download_corpora.WebDriverWait", _Wait)

    with pytest.raises(PermissionError, match="Invalid password"):
        login_and_get_cookies("user@example.com", "secret")

    assert driver.quit_called


class _Response:
    def __init__(self, text="", status_code=200, headers=None, chunks=None, broken=False):
        self.text = text
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = chunks or []
        self._broken = broken

    def raise_for_status(self):
        if self._broken or self.status_code >= 400:
            raise RuntimeError("request failed")

    def iter_content(self, chunk_size=65536):
        yield from self._chunks


class _Session:
    def __init__(self, pages):
        self.pages = pages

    def get(self, url, stream=False, timeout=None):
        page = self.pages[url]
        if isinstance(page, Exception):
            raise page
        return page


def test_corpus_names_keep_childes_order_and_add_new_phon_names():
    session = _Session(
        {
            INDEX_URL: _Response(
                '<a href="Brent.html">Brent</a>'
                '<a href="subdir/Bloom.html">skip</a>'
                '<a href="notes.txt">skip</a>'
            ),
            PHON_INDEX_URL: _Response(
                '<a href="brent.html">duplicate</a><a href="PhonOnly.html">Phon</a>'
            ),
        }
    )

    assert _corpus_names_from_index(session, INDEX_URL) == ["Brent"]
    assert fetch_corpus_names(session) == ["Brent", "PhonOnly"]


def test_zip_links_skip_failed_pages_and_keep_zip_anchors():
    missing = _Session({INDEX_URL: _Response(status_code=404)})
    broken = _Session({INDEX_URL: _Response(status_code=200, broken=True)})
    page = _Session(
        {
            INDEX_URL: _Response(
                '<a href="/childes/data/Eng-NA/Brent.zip?f=zip">CHAT</a>'
                '<a href="https://files.example/other.zip?f=zip">Audio</a>'
                '<a href="readme.html">skip</a>'
            )
        }
    )

    assert _zip_links_from_page(missing, INDEX_URL) == []
    assert _zip_links_from_page(broken, INDEX_URL) == []
    assert _zip_links_from_page(page, INDEX_URL) == [
        ("chat", f"{BASE_URL}/childes/data/Eng-NA/Brent.zip?f=zip"),
        ("audio", "https://files.example/other.zip?f=zip"),
    ]


def test_fetch_download_url_prefers_childes_then_phon_chat():
    childes_page = f"{INDEX_URL}Brent.html"
    phon_page = f"{PHON_INDEX_URL}Phon.html"
    plain_page = f"{PHON_INDEX_URL}Audio.html"
    session = _Session(
        {
            childes_page: _Response(
                '<a href="/childes/data/Eng-NA/Brent.zip?f=zip">CHAT</a>'
            ),
            phon_page: _Response(
                '<a href="/phon/data/other.zip?f=zip">Audio</a>'
                '<a href="/phon/data/Eng-NA/Phon.zip?f=zip">CHAT</a>'
            ),
            plain_page: _Response('<a href="/phon/data/audio.zip?f=zip">Audio</a>'),
            f"{INDEX_URL}Phon.html": _Response(""),
            f"{INDEX_URL}Audio.html": _Response(""),
            f"{INDEX_URL}Missing.html": _Response(""),
            f"{PHON_INDEX_URL}Missing.html": _Response(""),
        }
    )

    assert fetch_download_url(session, "Brent").endswith("Brent.zip?f=zip")
    assert "/Eng-NA/" in fetch_download_url(session, "Phon")
    assert fetch_download_url(session, "Audio").endswith("audio.zip?f=zip")
    assert fetch_download_url(session, "Missing") is None


def _zip_bytes(names):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name in names:
            archive.writestr(name, "contents")
    return buffer.getvalue()


def test_download_stream_rejects_html_and_a_slow_transfer(monkeypatch):
    html = _Session(
        {
            "https://files/corpus.zip": _Response(
                headers={"content-type": "text/html"},
                chunks=[b"<html>"],
            )
        }
    )
    with pytest.raises(PermissionError, match="HTML"):
        _download_stream(html, "https://files/corpus.zip")

    clock = {"tick": 0}

    def monotonic():
        clock["tick"] += 1
        return 0 if clock["tick"] == 1 else 16

    monkeypatch.setattr("src.cli.download_corpora.time.monotonic", monotonic)
    slow = _Session(
        {"https://files/corpus.zip": _Response(chunks=[b"x" * 100])}
    )
    with pytest.raises(TimeoutError, match="too slow"):
        _download_stream(slow, "https://files/corpus.zip")


def test_download_stream_accepts_a_transfer_that_stays_above_the_minimum(monkeypatch):
    clock = iter((0, 15))
    monkeypatch.setattr(
        "src.cli.download_corpora.time.monotonic",
        lambda: next(clock),
    )
    chunk = b"x" * (800 * 1024)
    session = _Session(
        {"https://files/corpus.zip": _Response(chunks=[chunk])}
    )

    assert _download_stream(session, "https://files/corpus.zip") == chunk


def test_download_stream_reports_progress_with_and_without_a_known_size(capsys):
    chunk = b"x" * (5 * 1024 * 1024)
    known = _Session(
        {
            "https://files/corpus.zip": _Response(
                headers={"content-length": str(len(chunk))},
                chunks=[chunk],
            )
        }
    )
    unknown = _Session(
        {"https://files/corpus.zip": _Response(chunks=[chunk])}
    )

    assert _download_stream(known, "https://files/corpus.zip") == chunk
    assert "100%" in capsys.readouterr().out
    assert _download_stream(unknown, "https://files/corpus.zip") == chunk
    assert "MB downloaded" in capsys.readouterr().out


def test_download_corpus_skips_an_existing_directory_and_a_missing_link(tmp_path, monkeypatch):
    existing = tmp_path / "Brent"
    existing.mkdir()

    assert download_corpus(_Session({}), "Brent", str(tmp_path), force=False) is False

    monkeypatch.setattr(
        "src.cli.download_corpora.fetch_download_url",
        lambda session, name: None,
    )
    assert download_corpus(_Session({}), "Missing", str(tmp_path), force=True) is False


def test_download_corpus_extracts_a_matching_root_and_retries(tmp_path, monkeypatch):
    calls = {"count": 0}

    def flaky_stream(session, url):
        calls["count"] += 1
        if calls["count"] == 1:
            raise TimeoutError("slow")
        return _zip_bytes(["Brent/child.cha"])

    monkeypatch.setattr("src.cli.download_corpora.fetch_download_url", lambda session, name: "https://files/brent.zip")
    monkeypatch.setattr("src.cli.download_corpora._download_stream", flaky_stream)
    monkeypatch.setattr("src.cli.download_corpora.time.sleep", lambda seconds: None)

    assert download_corpus(_Session({}), "Brent", str(tmp_path), force=False) is True
    assert (tmp_path / "Brent" / "child.cha").is_file()
    assert calls["count"] == 2


def test_download_corpus_extracts_into_the_corpus_folder_and_reraises(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.cli.download_corpora.fetch_download_url",
        lambda session, name: "https://files/other.zip",
    )
    monkeypatch.setattr(
        "src.cli.download_corpora._download_stream",
        lambda session, url: _zip_bytes(["other/child.cha"]),
    )

    assert download_corpus(_Session({}), "Brent", str(tmp_path), force=False) is True
    assert (tmp_path / "Brent" / "other" / "child.cha").is_file()

    monkeypatch.setattr(
        "src.cli.download_corpora._download_stream",
        lambda session, url: (_ for _ in ()).throw(TimeoutError("still slow")),
    )
    with pytest.raises(TimeoutError, match="still slow"):
        download_corpus(_Session({}), "Bloom", str(tmp_path), force=False, retries=0)


def test_run_downloads_every_listed_corpus_when_no_filter_is_given(
    tmp_path, capsys, monkeypatch
):
    monkeypatch.setattr(
        "src.cli.download_corpora.login_and_get_cookies",
        lambda email, password, headless: {"session": "abc"},
    )
    monkeypatch.setattr(
        "src.cli.download_corpora.fetch_corpus_names",
        lambda session: ["Brent"],
    )
    monkeypatch.setattr(
        "src.cli.download_corpora.download_corpus",
        lambda session, corpus_name, output_dir, force: True,
    )

    run("user@example.com", "secret", None, str(tmp_path), force=False)

    assert "1 downloaded, 0 skipped, 0 failed" in capsys.readouterr().out


def test_run_stops_when_login_is_rejected(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        "src.cli.download_corpora.login_and_get_cookies",
        lambda email, password, headless: (_ for _ in ()).throw(
            PermissionError("denied")
        ),
    )

    run("user@example.com", "secret", None, str(tmp_path), force=False)

    assert "ERROR: denied" in capsys.readouterr().out


def test_run_counts_downloads_skips_and_failures(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(
        "src.cli.download_corpora.login_and_get_cookies",
        lambda email, password, headless: {"session": "abc"},
    )
    monkeypatch.setattr(
        "src.cli.download_corpora.fetch_corpus_names",
        lambda session: ["Brent", "Bloom", "Brown", "Post"],
    )

    def fake_download(session, corpus_name, output_dir, force):
        if corpus_name == "Brent":
            return True
        if corpus_name == "Bloom":
            return False
        if corpus_name == "Brown":
            raise PermissionError("no access")
        raise RuntimeError("disk full")

    monkeypatch.setattr("src.cli.download_corpora.download_corpus", fake_download)

    run(
        "user@example.com",
        "secret",
        ["brent", "missing", "Bloom", "Brown", "Post"],
        str(tmp_path),
        force=True,
        headless=False,
    )

    output = capsys.readouterr().out
    assert "missing" in output
    assert "1 downloaded, 1 skipped, 2 failed" in output
