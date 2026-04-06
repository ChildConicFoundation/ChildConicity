from src.corpus_normalizers.hslld_normalizer import (
    extract_age,
    extract_child_name,
    has_target_child,
    process_directory,
)


def test_extract_child_name_from_hslld_filename():
    assert extract_child_name("Corpus/HSLLD/HV5/BR/jambr5.cha") == "jam"
    assert extract_child_name("Corpus/HSLLD/HV1/BR/gilbr1a.cha") == "gil"
    assert extract_child_name("Corpus/HSLLD/HV3/MT/trimt3pt2.cha") == "tri"


def test_extract_age_accepts_missing_day(tmp_path):
    file_path = tmp_path / "jambr5.cha"
    file_path.write_text(
        "@ID:\teng|HSLLD|CHI|7;05.|male|||Target_Child|||\n",
        encoding="utf-8",
    )

    assert extract_age(str(file_path)) == "7 years 05 months 00 days"


def test_process_directory_groups_by_child_and_filters_non_target_files(tmp_path):
    source_dir = tmp_path / "Corpus" / "HSLLD"
    target_dir = tmp_path / "Corpus_modified" / "HSLLD"

    valid_br_dir = source_dir / "HV1" / "BR"
    valid_mt_dir = source_dir / "HV1" / "MT"
    invalid_dir = source_dir / "HV1" / "ACT"
    valid_br_dir.mkdir(parents=True)
    valid_mt_dir.mkdir(parents=True)
    invalid_dir.mkdir(parents=True)

    (valid_br_dir / "jambr1.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: CHI Target_Child, MOT Mother
@ID: eng|HSLLD|CHI|3;07.08|male|||Target_Child|||
@ID: eng|HSLLD|MOT||female|||Mother|||
*CHI: hi .
""",
        encoding="utf-8",
    )
    (valid_mt_dir / "jammt1.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: CHI Target_Child, SIS Sister
@ID: eng|HSLLD|CHI|3;07.09|male|||Target_Child|||
@ID: eng|HSLLD|SIS|||||Sister|||
*CHI: hi .
""",
        encoding="utf-8",
    )
    (invalid_dir / "anaact1.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: PAR1 Participant, PAR2 Participant
@ID: eng|HSLLD|PAR1|||||Participant|||
@ID: eng|HSLLD|PAR2|||||Participant|||
*PAR1: hi .
""",
        encoding="utf-8",
    )

    assert has_target_child(str(valid_br_dir / "jambr1.cha")) is True
    assert has_target_child(str(invalid_dir / "anaact1.cha")) is False

    process_directory(str(source_dir), str(target_dir))

    grouped_files = sorted((target_dir / "jam").iterdir())
    assert [path.name for path in grouped_files] == ["jambr1.cha", "jammt1.cha"]
    assert not (target_dir / "ana").exists()

    jambr1_content = (target_dir / "jam" / "jambr1.cha").read_text(encoding="utf-8")
    assert "@ChildName: jam" in jambr1_content
    assert "@ChildAge: 3 years 07 months 08 days" in jambr1_content
