def prepare_corpus_cli_options(options, available_corpora, writer=print):
    if options.list_corpora:
        writer("\nCorpus disponibles:")
        for corpus_name in available_corpora:
            writer(f"- {corpus_name}")
        return options, True

    validated_options = options.validate_against(available_corpora)

    if validated_options.corpora is None:
        writer("\nTrabajando con todos los corpus disponibles.")
    else:
        writer(
            "\nTrabajando con estos corpus: "
            + ", ".join(validated_options.corpora)
        )

    return validated_options, False
