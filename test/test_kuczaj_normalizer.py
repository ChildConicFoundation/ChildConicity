from src.corpus_normalizers.kuczaj_normalizer import extract_age, process_directory


def test_extract_age_supports_missing_day_for_kuczaj(tmp_path):
    file_path = tmp_path / "020500.cha"
    file_path.write_text(
        "@ID:\teng|Kuczaj|CHI|2;05.|male|TD||Target_Child|||\n",
        encoding="utf-8",
    )

    assert extract_age(str(file_path)) == "2 years 05 months 00 days"


def test_process_directory_groups_flat_kuczaj_files_under_abe(tmp_path):
    source_dir = tmp_path / "Corpus" / "Kuczaj"
    target_dir = tmp_path / "Corpora_modified" / "Kuczaj"
    source_dir.mkdir(parents=True)

    (source_dir / "020424.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: FAT Father, CHI Target_Child
@ID: eng|Kuczaj|FAT||male|||Father|||
@ID: eng|Kuczaj|CHI|2;04.24|male|TD||Target_Child|||
*CHI: hi .
""",
        encoding="utf-8",
    )
    (source_dir / "020500.cha").write_text(
        """@UTF8
@PID: test
@Begin
@Languages: eng
@Participants: FAT Father, CHI Target_Child
@ID: eng|Kuczaj|FAT||male|||Father|||
@ID: eng|Kuczaj|CHI|2;05.|male|TD||Target_Child|||
*CHI: hi .
""",
        encoding="utf-8",
    )

    process_directory(str(source_dir), str(target_dir))

    target_child_dir = target_dir / "Abe"
    assert sorted(path.name for path in target_child_dir.iterdir()) == [
        "020424.cha",
        "020500.cha",
    ]

    first_content = (target_child_dir / "020424.cha").read_text(encoding="utf-8")
    second_content = (target_child_dir / "020500.cha").read_text(encoding="utf-8")

    assert "@ChildName: Abe" in first_content
    assert "@ChildAge: 2 years 04 months 24 days" in first_content
    assert "@ChildAge: 2 years 05 months 00 days" in second_content
