import pytest

from src.cli.download_corpora import (
    TALKBANK_PASSWORD_ENV,
    TALKBANK_USER_ENV,
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


def test_run_reports_each_corpus_and_returns_summary(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "src.cli.download_corpora.login_and_get_cookies",
        lambda *args, **kwargs: {"session": "ok"},
    )
    monkeypatch.setattr(
        "src.cli.download_corpora.fetch_corpus_names",
        lambda session: ["Brent", "Bloom"],
    )
    monkeypatch.setattr(
        "src.cli.download_corpora.download_corpus",
        lambda *args, **kwargs: True,
    )
    seen = []

    summary = run(
        "person@example.com",
        "secret-value",
        ["Brent"],
        str(tmp_path),
        False,
        on_corpus=lambda name, index, total: seen.append((name, index, total)),
    )

    assert seen == [("Brent", 1, 1)]
    assert summary == {
        "downloaded": 1,
        "skipped": 0,
        "failed": 0,
        "requested": ["Brent"],
        "error": None,
    }
    assert "secret-value" not in str(summary)


def test_run_returns_login_error(monkeypatch, tmp_path):
    def reject_login(*args, **kwargs):
        raise PermissionError("Authentication error: rejected")

    monkeypatch.setattr("src.cli.download_corpora.login_and_get_cookies", reject_login)

    summary = run(
        "person@example.com",
        "secret-value",
        ["Brent"],
        str(tmp_path),
        False,
    )

    assert summary["error"] == "login"
    assert summary["downloaded"] == 0
    assert "secret-value" not in str(summary)
