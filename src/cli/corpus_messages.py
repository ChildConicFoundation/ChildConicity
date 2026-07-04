def prepare_corpus_cli_options(options, available_corpora, writer=print):
    if options.list_corpora:
        writer("\nAvailable corpora:")
        for corpus_name in available_corpora:
            writer(f"- {corpus_name}")
        return options, True

    validated_options = options.validate_against(available_corpora)

    if validated_options.corpora is None:
        writer("\nWorking with all available corpora.")
    else:
        writer(
            "\nWorking with these corpora: "
            + ", ".join(validated_options.corpora)
        )

    return validated_options, False
