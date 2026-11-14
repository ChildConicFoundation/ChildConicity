from src.corpus_normalizers.bloom_normalizer import (
    extract_age as bloom_extract_age,
    process_directory as bloom_process_directory,
)
from src.corpus_normalizers.brown_normalizer import (
    process_directory as brown_process_directory,
)
from src.corpus_normalizers.post_normalizer import (
    extract_age as post_extract_age,
    process_directory as post_process_directory,
)
from src.corpus_normalizers.providence_normalizer import (
    extract_age as providence_extract_age,
    process_directory as providence_process_directory,
)


def _write_child_file(directory, corpus_name):
    directory.mkdir(parents=True)
    cha_file = directory / "child.cha"
    cha_file.write_text(
        "@Languages:\teng\n"
        f"@ID:\teng|{corpus_name}|CHI|1;06.02|female|||\n",
        encoding="utf-8",
    )
    (directory / "notes.txt").write_text("not a transcript", encoding="utf-8")


def test_bloom_and_providence_read_the_age_for_their_corpus(tmp_path):
    bloom = tmp_path / "bloom.cha"
    providence = tmp_path / "providence.cha"
    bloom.write_text("@ID:\teng|Bloom|CHI|2;03.|male|||\n", encoding="utf-8")
    providence.write_text(
        "@ID:\teng|Providence|CHI|1;11.09|female|||\n",
        encoding="utf-8",
    )
    post = tmp_path / "post.cha"
    post.write_text("@ID:\teng|Post|CHI|3;00.01|male|||\n", encoding="utf-8")

    assert bloom_extract_age(str(bloom)) == "2 years 03 months 00 days"
    assert providence_extract_age(str(providence)) == "1 years 11 months 09 days"
    assert post_extract_age(str(post)) == "3 years 00 months 01 days"


def test_shared_child_subdir_normalizers_copy_transcripts(tmp_path):
    source = tmp_path / "source"
    _write_child_file(source / "Peter", "Bloom")
    bloom_process_directory(str(source), str(tmp_path / "bloom"))
    bloom_copy = (tmp_path / "bloom" / "Peter" / "child.cha").read_text(encoding="utf-8")
    assert "@ChildName: Peter" in bloom_copy
    assert "2 years" not in bloom_copy
    assert "1 years 06 months 02 days" in bloom_copy

    source = tmp_path / "brown-source"
    _write_child_file(source / "Adam", "Brown")
    brown_process_directory(str(source), str(tmp_path / "brown"))
    assert "@ChildName: Adam" in (
        tmp_path / "brown" / "Adam" / "child.cha"
    ).read_text(encoding="utf-8")

    source = tmp_path / "providence-source"
    _write_child_file(source / "Ethan", "Providence")
    providence_process_directory(str(source), str(tmp_path / "providence"))
    assert "@ChildName: Ethan" in (
        tmp_path / "providence" / "Ethan" / "child.cha"
    ).read_text(encoding="utf-8")

    source = tmp_path / "post-source"
    _write_child_file(source / "Naomi", "Post")
    post_process_directory(str(source), str(tmp_path / "post"))
    assert "@ChildName: Naomi" in (
        tmp_path / "post" / "Naomi" / "child.cha"
    ).read_text(encoding="utf-8")
