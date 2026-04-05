from src.cli import (
    CorpusCLIOptions,
    parse_corpus_cli_options,
    prepare_corpus_cli_options,
)


def test_parse_corpus_cli_options_supports_all():
    options = parse_corpus_cli_options(["--corpora", "all"])

    assert options.corpora is None
    assert options.list_corpora is False


def test_parse_corpus_cli_options_supports_lists_and_commas():
    options = parse_corpus_cli_options(["--corpora", "Brent,Post", "newengland"])

    assert options.corpora == ["brent", "post", "newengland"]


def test_corpus_cli_options_validate_against_available_corpora():
    options = CorpusCLIOptions(corpora=["brent", "post"])

    validated_options = options.validate_against(["Brent", "Post", "VanKleeck"])

    assert validated_options.corpora == ["Brent", "Post"]


def test_corpus_cli_options_rejects_invalid_mixed_all_selection():
    try:
        parse_corpus_cli_options(["--corpora", "all", "Brent"])
    except ValueError as exc:
        assert "Usa 'all' por separado" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError al mezclar 'all' con corpus.")


def test_corpus_cli_options_rejects_unknown_corpora():
    options = CorpusCLIOptions(corpora=["brent", "foo"])

    try:
        options.validate_against(["Brent", "Post"])
    except ValueError as exc:
        assert "foo" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError al usar un corpus inexistente.")


def test_prepare_corpus_cli_options_lists_corpora_and_exits():
    messages = []
    options = CorpusCLIOptions(corpora=None, list_corpora=True)

    prepared_options, should_exit = prepare_corpus_cli_options(
        options, ["Brent", "Post"], writer=messages.append
    )

    assert prepared_options == options
    assert should_exit is True
    assert messages == [
        "\nCorpus disponibles:",
        "- Brent",
        "- Post",
    ]


def test_prepare_corpus_cli_options_reports_selected_corpora():
    messages = []
    options = CorpusCLIOptions(corpora=["brent", "post"])

    prepared_options, should_exit = prepare_corpus_cli_options(
        options, ["Brent", "Post", "VanKleeck"], writer=messages.append
    )

    assert should_exit is False
    assert prepared_options.corpora == ["Brent", "Post"]
    assert messages == ["\nTrabajando con estos corpus: Brent, Post"]
