from pathlib import Path

import pytest

from src.cli.download_iconicity_ratings import download_iconicity_ratings


VALID_CSV = (
    b"word,n_ratings,n,prop_known,rating,rating_sd\n"
    b"ball,10,10,1,5.8,1.2\n"
)


class FakeResponse:
    def __init__(self, content, status_error=None):
        self.content = content
        self.status_error = status_error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        if self.status_error:
            raise self.status_error

    def iter_content(self, chunk_size):
        yield self.content


class FakeSession:
    def __init__(self, content):
        self.content = content
        self.calls = []

    def get(self, url, stream, timeout):
        self.calls.append({"url": url, "stream": stream, "timeout": timeout})
        return FakeResponse(self.content)


def test_download_iconicity_ratings_writes_valid_csv(tmp_path):
    output_path = tmp_path / "iconicity_ratings_cleaned.csv"
    session = FakeSession(VALID_CSV)

    downloaded = download_iconicity_ratings(
        output_path=output_path,
        session=session,
    )

    assert downloaded is True
    assert output_path.read_bytes() == VALID_CSV
    assert session.calls == [
        {
            "url": "https://osf.io/ex37k/download",
            "stream": True,
            "timeout": (20, 60),
        }
    ]


def test_download_iconicity_ratings_skips_existing_file_without_force(tmp_path):
    output_path = tmp_path / "iconicity_ratings_cleaned.csv"
    output_path.write_text("already here", encoding="utf-8")
    session = FakeSession(VALID_CSV)

    downloaded = download_iconicity_ratings(
        output_path=output_path,
        session=session,
    )

    assert downloaded is False
    assert output_path.read_text(encoding="utf-8") == "already here"
    assert session.calls == []


def test_download_iconicity_ratings_replaces_existing_file_with_force(tmp_path):
    output_path = tmp_path / "iconicity_ratings_cleaned.csv"
    output_path.write_text("old content", encoding="utf-8")

    downloaded = download_iconicity_ratings(
        output_path=output_path,
        force=True,
        session=FakeSession(VALID_CSV),
    )

    assert downloaded is True
    assert output_path.read_bytes() == VALID_CSV


def test_download_iconicity_ratings_rejects_unexpected_csv(tmp_path):
    output_path = tmp_path / "iconicity_ratings_cleaned.csv"
    session = FakeSession(b"word,rating\nball,5.8\n")

    with pytest.raises(ValueError, match="Missing columns"):
        download_iconicity_ratings(output_path=output_path, session=session)

    assert not output_path.exists()
    assert not Path(f"{output_path}.tmp").exists()
