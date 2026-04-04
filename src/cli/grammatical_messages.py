def prepare_grammatical_cli_options(options, available_categories, writer=print):
    if options.list_categories:
        writer("\nCategorías gramaticales disponibles:")
        for category in available_categories:
            writer(f"- {category}")
        return options, True

    validated_options = options.validate_against(available_categories)

    if validated_options.categories is None:
        writer("\nTrabajando con todas las categorías gramaticales.")
    else:
        writer(
            "\nTrabajando con estas categorías gramaticales: "
            + ", ".join(validated_options.categories)
        )

    return validated_options, False
