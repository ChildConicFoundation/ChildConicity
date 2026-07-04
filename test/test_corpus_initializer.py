from unittest.mock import patch
from pathlib import Path

import pytest

from src.corpus_initialization import CorpusInitializer


def test_corpus_initializer_initialize_all_uses_source_and_output_roots(tmp_path):
    source_root = tmp_path / "source"
    output_root = tmp_path / "output"
    initializer = CorpusInitializer(
        source_root=str(source_root),
        output_root=str(output_root),
    )

    with patch(
        "src.corpus_initialization.initializer.process_bates"
    ) as mock_bates, patch(
        "src.corpus_initialization.initializer.BrendManipulator"
    ) as mock_brend_manipulator, patch(
        "src.corpus_initialization.initializer.process_newengland"
    ) as mock_newengland, patch(
        "src.corpus_initialization.initializer.process_post"
    ) as mock_post, patch(
        "src.corpus_initialization.initializer.process_bloom"
    ) as mock_bloom, patch(
        "src.corpus_initialization.initializer.process_brown"
    ) as mock_brown, patch(
        "src.corpus_initialization.initializer.process_hslld"
    ) as mock_hslld, patch(
        "src.corpus_initialization.initializer.process_kuczaj"
    ) as mock_kuczaj, patch(
        "src.corpus_initialization.initializer.process_sachs"
    ) as mock_sachs, patch(
        "src.corpus_initialization.initializer.process_vankleeck"
    ) as mock_vankleeck, patch(
        "src.corpus_initialization.initializer.process_providence"
    ) as mock_providence:
        manipulator_instance = mock_brend_manipulator.return_value

        initializer.initialize_all()

    assert manipulator_instance.base_dir == str(source_root / "Brent")
    assert manipulator_instance.output_dir == str(output_root / ".Brent.pending")
    manipulator_instance.process_directory.assert_called_once_with()
    mock_newengland.assert_called_once_with(
        str(source_root / "NewEngland"),
        str(output_root / ".NewEngland.pending"),
    )
    mock_post.assert_called_once_with(
        str(source_root / "Post"),
        str(output_root / ".Post.pending"),
    )
    mock_bloom.assert_called_once_with(
        str(source_root / "Bloom"),
        str(output_root / ".Bloom.pending"),
    )
    mock_brown.assert_called_once_with(
        str(source_root / "Brown"),
        str(output_root / ".Brown.pending"),
    )
    mock_hslld.assert_called_once_with(
        str(source_root / "HSLLD"),
        str(output_root / ".HSLLD.pending"),
    )
    mock_kuczaj.assert_called_once_with(
        str(source_root / "Kuczaj"),
        str(output_root / ".Kuczaj.pending"),
    )
    mock_sachs.assert_called_once_with(
        str(source_root / "Sachs"),
        str(output_root / ".Sachs.pending"),
    )
    mock_vankleeck.assert_called_once_with(
        str(source_root / "VanKleeck"),
        str(output_root / ".VanKleeck.pending"),
    )
    mock_providence.assert_called_once_with(
        str(source_root / "Providence"),
        str(output_root / ".Providence.pending"),
    )
    mock_bates.assert_called_once_with(
        str(source_root / "Bates"),
        str(output_root / ".Bates.pending"),
    )


def test_corpus_initializer_removes_pending_output_after_failure(tmp_path):
    source_root = tmp_path / "source"
    output_root = tmp_path / "Corpora_modified"
    source_root.mkdir()
    output_root.mkdir()
    existing_output = output_root / "Bates"
    existing_output.mkdir()
    (existing_output / "existing.cha").write_text("keep me", encoding="utf-8")

    initializer = CorpusInitializer(
        source_root=str(source_root),
        output_root=str(output_root),
    )

    def failing_processor(_source_dir, target_dir):
        target = Path(target_dir) / "partial.cha"
        target.write_text("partial", encoding="utf-8")
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        initializer._initialize_corpus("Bates", failing_processor)

    assert not (output_root / ".Bates.pending").exists()
    assert (existing_output / "existing.cha").read_text(encoding="utf-8") == "keep me"
