import textwrap

import pytest

from src.corpus_normalizers.bates_normalizer import (
    _child_name,
    extract_age,
    process_directory,
)

# ---------------------------------------------------------------------------
# _child_name
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("stem,expected", [
    ("amy",      "Amy"),
    ("amy28",    "Amy"),
    ("amyst",    "Amy"),
    ("ed_snack", "Ed"),
    ("george28", "George"),
    ("georgest", "George"),
    ("kent",     "Kent"),
    ("kent28",   "Kent"),
    ("kentst",   "Kent"),
    ("will",     "Will"),
    ("will28",   "Will"),
    ("willst",   "Will"),
])
def test_child_name_strips_session_suffix(stem, expected):
    assert _child_name(stem) == expected


# ---------------------------------------------------------------------------
# extract_age
# ---------------------------------------------------------------------------

_CHA_WITH_AGE = textwrap.dedent("""\
    @UTF8
    @Begin
    @Languages: eng
    @Participants: MOT Mother, CHI Target_Child
    @ID: eng|Bates|CHI|1;08.|female|TD|MC|Target_Child|||
""")

_CHA_NO_DAYS = textwrap.dedent("""\
    @UTF8
    @Begin
    @Languages: eng
    @ID: eng|Bates|CHI|2;04.|female|TD|MC|Target_Child|||
""")

_CHA_NO_AGE = textwrap.dedent("""\
    @UTF8
    @Begin
    @Languages: eng
    @ID: eng|Bates|MOT||female|||Mother|||
""")


def test_extract_age_parses_years_and_months(tmp_path):
    f = tmp_path / "amy.cha"
    f.write_text(_CHA_WITH_AGE)
    assert extract_age(str(f)) == "1 years 08 months 00 days"


def test_extract_age_zero_days_when_missing(tmp_path):
    f = tmp_path / "amy28.cha"
    f.write_text(_CHA_NO_DAYS)
    assert extract_age(str(f)) == "2 years 04 months 00 days"


def test_extract_age_returns_none_when_no_chi_id(tmp_path):
    f = tmp_path / "mot.cha"
    f.write_text(_CHA_NO_AGE)
    assert extract_age(str(f)) is None


def test_extract_age_returns_none_for_missing_file():
    assert extract_age("/nonexistent/path.cha") is None


# ---------------------------------------------------------------------------
# process_directory
# ---------------------------------------------------------------------------

_CHA_CONTENT = textwrap.dedent("""\
    @UTF8
    @Begin
    @Languages: eng
    @Participants: MOT Mother, CHI Target_Child
    @ID: eng|Bates|CHI|1;08.|female|TD|MC|Target_Child|||
    *CHI: hi .
    @End
""")


def test_process_directory_copies_and_injects_metadata(tmp_path):
    src = tmp_path / "source" / "Bates"
    session = src / "Free20"
    session.mkdir(parents=True)
    (session / "amy.cha").write_text(_CHA_CONTENT)

    tgt = tmp_path / "output" / "Bates"

    process_directory(str(src), str(tgt))

    out_file = tgt / "Free20" / "amy.cha"
    assert out_file.exists()
    content = out_file.read_text()
    assert "@ChildName: Amy" in content
    assert "@ChildAge: 1 years 08 months 00 days" in content


def test_process_directory_handles_all_session_suffix_variants(tmp_path):
    src = tmp_path / "source" / "Bates"
    for session, fname in [("Free20", "amy.cha"), ("Free28", "amy28.cha"), ("Story28", "amyst.cha")]:
        d = src / session
        d.mkdir(parents=True)
        (d / fname).write_text(_CHA_CONTENT)

    tgt = tmp_path / "output" / "Bates"
    process_directory(str(src), str(tgt))

    for session, fname in [("Free20", "amy.cha"), ("Free28", "amy28.cha"), ("Story28", "amyst.cha")]:
        content = (tgt / session / fname).read_text()
        assert "@ChildName: Amy" in content


def test_process_directory_skips_non_cha_files(tmp_path):
    src = tmp_path / "source" / "Bates" / "Free20"
    src.mkdir(parents=True)
    (src / "readme.txt").write_text("not a cha file")
    (src / "amy.cha").write_text(_CHA_CONTENT)

    tgt = tmp_path / "output" / "Bates"
    process_directory(str(src.parent), str(tgt))

    assert not (tgt / "Free20" / "readme.txt").exists()
    assert (tgt / "Free20" / "amy.cha").exists()
