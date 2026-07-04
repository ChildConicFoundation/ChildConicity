import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_initialize_corpuses_module():
    module_path = PROJECT_ROOT / "examples" / "initialize_corpuses.py"
    spec = importlib.util.spec_from_file_location("initialize_corpuses", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def initialize_corpuses():
    return _load_initialize_corpuses_module()


def test_main_uses_default_roots_when_called_programmatically(initialize_corpuses):
    with patch.object(initialize_corpuses, "CorpusInitializer") as mock_initializer_cls:
        mock_initializer = mock_initializer_cls.return_value

        exit_code = initialize_corpuses.main()

    assert exit_code == 0
    mock_initializer_cls.assert_called_once_with(
        source_root=initialize_corpuses.DEFAULT_SOURCE_ROOT,
        output_root=initialize_corpuses.DEFAULT_OUTPUT_ROOT,
    )
    mock_initializer.initialize_all.assert_called_once_with()


def test_main_parses_custom_roots_from_argv(initialize_corpuses):
    with patch.object(initialize_corpuses, "CorpusInitializer") as mock_initializer_cls:
        mock_initializer = mock_initializer_cls.return_value

        exit_code = initialize_corpuses.main(
            [
                "--source-root",
                "/tmp/source",
                "--output-root",
                "/tmp/output",
            ]
        )

    assert exit_code == 0
    mock_initializer_cls.assert_called_once_with(
        source_root="/tmp/source",
        output_root="/tmp/output",
    )
    mock_initializer.initialize_all.assert_called_once_with()


def test_main_uses_defaults_when_argv_is_empty(initialize_corpuses):
    with patch.object(initialize_corpuses, "CorpusInitializer") as mock_initializer_cls:
        exit_code = initialize_corpuses.main([])

    assert exit_code == 0
    mock_initializer_cls.assert_called_once_with(
        source_root=initialize_corpuses.DEFAULT_SOURCE_ROOT,
        output_root=initialize_corpuses.DEFAULT_OUTPUT_ROOT,
    )
