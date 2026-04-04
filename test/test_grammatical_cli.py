from src.cli import (
    GrammaticalCLIOptions,
    parse_grammatical_cli_options,
    prepare_grammatical_cli_options,
)


def test_parse_grammatical_cli_options_supports_all():
    options = parse_grammatical_cli_options(["--categories", "all"])

    assert options.categories is None
    assert options.list_categories is False
    assert options.output_dir == "quarterly_grammatical_categories"


def test_parse_grammatical_cli_options_supports_lists_and_commas():
    options = parse_grammatical_cli_options(["--categories", "noun,verb", "Adj"])

    assert options.categories == ["noun", "verb", "adj"]


def test_grammatical_cli_options_validate_against_available_categories():
    options = GrammaticalCLIOptions(categories=["noun", "verb"])

    validated_options = options.validate_against(["adj", "noun", "verb"])

    assert validated_options.categories == ["noun", "verb"]


def test_grammatical_cli_options_rejects_invalid_mixed_all_selection():
    try:
        parse_grammatical_cli_options(["--categories", "all", "noun"])
    except ValueError as exc:
        assert "Usa 'all' por separado" in str(exc)
    else:
        raise AssertionError("Se esperaba ValueError al mezclar 'all' con categorías.")


def test_grammatical_cli_options_rejects_unknown_categories():
    options = GrammaticalCLIOptions(categories=["noun", "verb"])

    try:
        options.validate_against(["noun", "adj"])
    except ValueError as exc:
        assert "verb" in str(exc)
    else:
        raise AssertionError(
            "Se esperaba ValueError al usar una categoría inexistente."
        )


def test_prepare_grammatical_cli_options_lists_categories_and_exits():
    messages = []
    options = GrammaticalCLIOptions(categories=None, list_categories=True)

    prepared_options, should_exit = prepare_grammatical_cli_options(
        options, ["adj", "noun"], writer=messages.append
    )

    assert prepared_options == options
    assert should_exit is True
    assert messages == [
        "\nCategorías gramaticales disponibles:",
        "- adj",
        "- noun",
    ]


def test_prepare_grammatical_cli_options_reports_selected_categories():
    messages = []
    options = GrammaticalCLIOptions(categories=["noun", "verb"])

    prepared_options, should_exit = prepare_grammatical_cli_options(
        options, ["adj", "noun", "verb"], writer=messages.append
    )

    assert should_exit is False
    assert prepared_options.categories == ["noun", "verb"]
    assert messages == [
        "\nTrabajando con estas categorías gramaticales: noun, verb"
    ]
