from unittest.mock import patch

import pytest

from src.data_io.corpus_inspector import (
    print_directory_structure,
    print_metadata,
    print_sampled_metadata,
    show_lew_early_expressions,
)
from src.data_io.corpus_processing import process_data_with_formatter


def test_process_data_with_formatter_preserves_structure_and_splits_speakers():
    corpus_data = {
        "Corpora_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {"metadata": {"file_path": "Corpora_modified/Post/Lew/a.cha", "child_name": "Lew"}},
                        {"metadata": {"file_path": "Corpora_modified/Post/Lew/readme.txt", "child_name": "Lew"}},
                    ]
                }
            }
        }
    }

    with patch("src.data_io.corpus_processing.DataFormatter.format_cha_data_from") as mock_format:
        mock_format.return_value = (
            {"1": {"text": "ball"}},
            {},
            {"1": {"text": "look"}},
        )
        result = process_data_with_formatter(corpus_data)

    files = result["Corpora_modified"]["Post"]["Lew"]["files"]
    assert len(files) == 1
    assert files[0]["children_data"]["1"]["text"] == "ball"
    assert files[0]["other_children_data"] == {}
    assert files[0]["adults_data"]["1"]["text"] == "look"
    assert files[0]["metadata"]["file_path"].endswith(".cha")


def test_process_data_with_formatter_includes_bates_and_providence():
    corpus_data = {
        "Corpora_modified": {
            "Bates": {
                "Amy": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpora_modified/Bates/Amy/a.cha",
                            }
                        }
                    ]
                }
            },
            "Providence": {
                "Alex": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpora_modified/Providence/Alex/a.cha",
                            }
                        }
                    ]
                }
            },
        }
    }

    with patch("src.data_io.corpus_processing.DataFormatter.format_cha_data_from") as mock_format:
        mock_format.return_value = ({"1": {"text": "ball"}}, {}, {})
        result = process_data_with_formatter(corpus_data)

    assert "Bates" in result["Corpora_modified"]
    assert "Providence" in result["Corpora_modified"]
    assert len(result["Corpora_modified"]["Bates"]["Amy"]["files"]) == 1
    assert len(result["Corpora_modified"]["Providence"]["Alex"]["files"]) == 1


def test_process_data_with_formatter_rejects_custom_root_key():
    corpus_data = {
        "MyCorpus": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "MyCorpus/Post/Lew/a.cha",
                            }
                        }
                    ]
                }
            }
        }
    }

    with pytest.raises(ValueError, match="Corpora_modified"):
        process_data_with_formatter(corpus_data)


def test_corpus_inspector_functions_print_expected_info(capsys):
    data = {
        "Corpora_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpora_modified/Post/Lew/a.cha",
                                "child_name": "Lew",
                                "child_age": "1 years 01 months 00 days",
                                "participants": {"CHI": "Target_Child"},
                                "types": ["toyplay"],
                                "utterances": [{"text": "ball"}],
                            }
                        }
                    ]
                }
            }
        }
    }

    print_directory_structure(data)
    print_metadata(data)
    print_sampled_metadata(data)
    captured = capsys.readouterr().out

    assert "Corpora_modified" in captured
    assert "Corpora_modified/Post/Lew/a.cha" in captured
    assert "Child name: Lew" in captured
    assert "First utterance: ball" in captured


def test_show_lew_early_expressions_handles_present_and_missing_data(capsys):
    processed_data = {
        "Corpora_modified": {
            "Post": {
                "Lew": {
                    "files": [
                        {
                            "metadata": {
                                "file_path": "Corpora_modified/Post/Lew/b.cha",
                                "child_age": "2 years 00 months 00 days",
                            },
                            "children_data": {"1": {"text": "later words"}},
                        },
                        {
                            "metadata": {
                                "file_path": "Corpora_modified/Post/Lew/a.cha",
                                "child_age": "1 years 00 months 00 days",
                            },
                            "children_data": {
                                "1": {"text": "first words", "timestamp": {"start": 1, "end": 2}}
                            },
                        },
                    ]
                }
            }
        }
    }

    show_lew_early_expressions(processed_data)
    show_lew_early_expressions({"Corpora_modified": {}})
    captured = capsys.readouterr().out

    assert "Lew early utterances" in captured
    assert "Corpora_modified/Post/Lew/a.cha" in captured
    assert "first words" in captured
    assert "Time: 1-2" in captured
