from unittest.mock import patch

from src.corpus_initialization import CorpusInitializer


def test_corpus_initializer_initialize_all_uses_source_and_output_roots():
    initializer = CorpusInitializer(
        source_root="/tmp/source",
        output_root="/tmp/output",
    )

    with patch(
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
        "src.corpus_initialization.initializer.process_vankleeck"
    ) as mock_vankleeck:
        manipulator_instance = mock_brend_manipulator.return_value

        initializer.initialize_all()

    assert manipulator_instance.base_dir == "/tmp/source/Brent"
    assert manipulator_instance.output_dir == "/tmp/output/Brent"
    manipulator_instance.process_directory.assert_called_once_with()
    mock_newengland.assert_called_once_with(
        "/tmp/source/NewEngland",
        "/tmp/output/NewEngland",
    )
    mock_post.assert_called_once_with(
        "/tmp/source/Post",
        "/tmp/output/Post",
    )
    mock_bloom.assert_called_once_with(
        "/tmp/source/Bloom",
        "/tmp/output/Bloom",
    )
    mock_brown.assert_called_once_with(
        "/tmp/source/Brown",
        "/tmp/output/Brown",
    )
    mock_vankleeck.assert_called_once_with(
        "/tmp/source/VanKleeck",
        "/tmp/output/VanKleeck",
    )
