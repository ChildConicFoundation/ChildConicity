def prepare_grammatical_cli_options(options, available_categories, writer=print):
    if options.list_categories:
        writer("\nAvailable grammatical categories:")
        for category in available_categories:
            writer(f"- {category}")
        return options, True

    validated_options = options.validate_against(available_categories)

    if validated_options.categories is None:
        writer("\nWorking with all grammatical categories.")
    else:
        writer(
            "\nWorking with these grammatical categories: "
            + ", ".join(validated_options.categories)
        )

    return validated_options, False
