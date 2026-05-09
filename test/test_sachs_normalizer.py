from src.corpus_normalizers.sachs_normalizer import extract_age, process_directory


def test_extract_age_supports_missing_day_for_sachs(tmp_path):
    file_path = tmp_path / "010800.cha"
    file_path.write_text(
        "@ID:\teng|Sachs|CHI|1;08.|female|||Target_Child|||\n",
        encoding="utf-8",
    )

    assert extract_age(str(file_path)) == "1 years 08 months 00 days"


def test_process_directory_groups_flat_sachs_files_under_naomi(tmp_path):
    source_dir = tmp_path / "Corpus" / "Sachs"
    target_dir = tmp_path / "Corpora_modified" / "Sachs"
    source_dir.mkdir(parents=True)

    (source_dir / "010229.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: MOT Mother, CHI Target_Child
@ID: eng|Sachs|MOT||female|||Mother|||
@ID: eng|Sachs|CHI|1;02.29|female|||Target_Child|||
*CHI: hi .
""",
        encoding="utf-8",
    )
    (source_dir / "010800.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: MOT Mother, CHI Target_Child
@ID: eng|Sachs|MOT||female|||Mother|||
@ID: eng|Sachs|CHI|1;08.|female|||Target_Child|||
*CHI: hi .
""",
        encoding="utf-8",
    )

    process_directory(str(source_dir), str(target_dir))

    target_child_dir = target_dir / "Naomi"
    assert sorted(path.name for path in target_child_dir.iterdir()) == [
        "010229.cha",
        "010800.cha",
    ]

    first_content = (target_child_dir / "010229.cha").read_text(encoding="utf-8")
    second_content = (target_child_dir / "010800.cha").read_text(encoding="utf-8")

    assert "@ChildName: Naomi" in first_content
    assert "@ChildAge: 1 years 02 months 29 days" in first_content
    assert "@ChildAge: 1 years 08 months 00 days" in second_content
