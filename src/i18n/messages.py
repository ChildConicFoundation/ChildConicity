MESSAGES = {
    "en": {
        "gui.language": "Language",
        "gui.language.en": "English",
        "gui.language.es": "Español",
        "gui.section.downloads": "Downloads",
        "gui.section.paths": "Paths",
        "gui.section.corpus": "Corpus",
        "gui.section.analysis_mode": "Analysis mode",
        "gui.section.grammatical_categories": "Grammatical categories",
        "gui.section.type_count": "How to count in type plots",
        "gui.section.rated": "Iconicity export (requires Types)",
        "gui.section.log": "Log",
        "gui.label.email_talkbank": "Email TalkBank",
        "gui.label.password": "Password",
        "gui.label.source_corpus": "Source corpus",
        "gui.label.processed_corpus": "Processed corpus",
        "gui.label.output_directory": "Output directory",
        "gui.label.quarterly_data": "Quarterly data",
        "gui.button.download_corpora": "Download corpora",
        "gui.button.download_ratings": "Download iconicity ratings",
        "gui.button.browse": "Browse...",
        "gui.button.initialize_corpora": "Initialize corpora",
        "gui.button.show_initialized": "Show initialized corpora",
        "gui.button.run_analysis": "Run analysis",
        "gui.button.generate_plots": "Generate plots",
        "gui.button.run_export": "Run export",
        "gui.checkbox.all_corpora": "All corpora",
        "gui.checkbox.all_categories": "All categories",
        "gui.radio.with_repetitions": "With repetitions",
        "gui.radio.once_per_form": "Once per form",
        "gui.help.corpora_select": "Select one or more corpora using the checkboxes:",
        "gui.help.categories_select": "Select one or more categories using the checkboxes:",
        "gui.help.rated": (
            "Enriches quarterly data with iconicity ratings and generates "
            "WordCount (with rating) and LemaCount (collapsed lemmas). "
            "Requires running the Types analysis first."
        ),
        "gui.help.type_count": (
            "Choose whether plots should use actual repetitions or count "
            "each form only once. This only affects Types plots; "
            "exported JSON files remain in standard format."
        ),
        "gui.empty.click_show_corpora": (
            "Click 'Show initialized corpora' to load available corpora."
        ),
        "gui.empty.click_show_or_wait": (
            "Click 'Show initialized corpora' or wait for categories to load."
        ),
        "gui.empty.no_categories": "No categories available.",
        "gui.empty.no_corpora": "No corpora available.",
        "gui.empty.processed_not_found": "Processed corpus folder not found.",
        "gui.status.ready": "Ready.",
        "gui.status.in_progress": "In progress...",
        "gui.error.title": "Error",
        "gui.error.talkbank_credentials": "Enter your TalkBank email and password.",
        "gui.error.set_processed_path": "Set the processed corpus path first.",
        "gui.error.select_category": (
            "Select at least one category or check 'All categories'."
        ),
        "gui.error.corpus_download": "Corpus download error",
        "gui.error.ratings_download": "Iconicity ratings download error",
        "gui.error.init_corpus": "Corpus initialization error",
        "gui.error.analysis": "Analysis error",
        "gui.info.in_progress": "In progress",
        "gui.notify.busy": "Another task is already running.",
        "gui.log.download_corpora_start": "\nStarting TalkBank corpus download...\n",
        "gui.log.download_complete": "\nDownload completed.\n",
        "gui.log.ratings_download_start": "\nStarting iconicity ratings download...\n",
        "gui.log.ratings_download_complete": "\nRatings download completed.\n",
        "gui.log.iconicity_export_start": "\nStarting iconicity export...\n",
        "gui.log.init_start": "\nStarting corpus initialization...\n",
        "gui.log.init_complete": "\nInitialization completed.\n",
        "gui.log.analysis_start": "\nStarting {action} for {corpora}...\n",
        "gui.log.iconicity_export_done": (
            "\nIconicity export completed. Results in: {path}\n"
        ),
        "gui.log.types_plots_done": "\nTypes plot generation completed.\n",
        "gui.log.types_plots_count_note": (
            "The selected counting criterion was applied only to "
            "plots; exported JSON files are unchanged.\n"
        ),
        "gui.log.types_plots_saved": "Types plots saved in: {path}\n",
        "gui.log.types_analysis_done": (
            "\nTypes analysis completed. Results exported to: {path}\n"
        ),
        "gui.log.token_plots_done": "\nToken plot generation completed.\n",
        "gui.log.plots_saved_pair": "Plots saved in: {plots} and {distribution}\n",
        "gui.log.token_analysis_done": (
            "\nToken analysis completed. Results exported to: {path}\n"
        ),
        "gui.log.corpora_refreshed": "Initialized corpora in {path}: {list}\n",
        "gui.log.categories_load_error": "Could not load categories: {error}",
        "gui.common.all_corpora": "all corpora",
        "gui.common.none": "(none)",
        "gui.rated.data_found": "Data found in: {path}",
        "gui.rated.no_data": "No quarterly data found. Run the Types analysis first.",
        "gui.validation.set_processed_path": "Set the processed corpus path first.",
        "gui.validation.processed_name": (
            "The processed corpus folder must be named {name}."
        ),
        "gui.validation.processed_missing": (
            "The processed corpus folder does not exist: {path}"
        ),
        "gui.validation.no_corpora": (
            "No processed corpora available in {path}. Initialize or refresh first."
        ),
        "gui.validation.missing_corpora": (
            "Missing processed corpora required to run analysis: {list}"
        ),
        "gui.validation.quarterly_missing": (
            "Quarterly data folder does not exist: {path}"
        ),
        "gui.action.tokens_plot_generation": "tokens plot generation",
        "gui.action.types_plot_generation": "types plot generation",
        "gui.action.tokens_analysis": "tokens analysis",
        "gui.action.types_analysis": "types analysis",
        "gui.error.no_interpreter": (
            "No interpreter is available with the dependencies required for analysis."
        ),
        "gui.error.external_exit": "External analysis exited with code {code}.",
    },
    "es": {
        "gui.language": "Idioma",
        "gui.language.en": "English",
        "gui.language.es": "Español",
        "gui.section.downloads": "Descargas",
        "gui.section.paths": "Rutas",
        "gui.section.corpus": "Corpus",
        "gui.section.analysis_mode": "Modo de análisis",
        "gui.section.grammatical_categories": "Categorías gramaticales",
        "gui.section.type_count": "Cómo contar en las gráficas de types",
        "gui.section.rated": "Exportación con iconicidad (requiere Types)",
        "gui.section.log": "Registro",
        "gui.label.email_talkbank": "Email TalkBank",
        "gui.label.password": "Contraseña",
        "gui.label.source_corpus": "Corpus origen",
        "gui.label.processed_corpus": "Corpus procesado",
        "gui.label.output_directory": "Directorio de salida",
        "gui.label.quarterly_data": "Datos trimestrales",
        "gui.button.download_corpora": "Descargar corpus",
        "gui.button.download_ratings": "Descargar ratings de iconicidad",
        "gui.button.browse": "Buscar...",
        "gui.button.initialize_corpora": "Inicializar corpus",
        "gui.button.show_initialized": "Mostrar corpus inicializados",
        "gui.button.run_analysis": "Ejecutar análisis",
        "gui.button.generate_plots": "Generar gráficas",
        "gui.button.run_export": "Ejecutar exportación",
        "gui.checkbox.all_corpora": "Todos los corpus",
        "gui.checkbox.all_categories": "Todas las categorías",
        "gui.radio.with_repetitions": "Con repeticiones",
        "gui.radio.once_per_form": "Una vez por forma",
        "gui.help.corpora_select": "Selecciona uno o varios corpus con casillas:",
        "gui.help.categories_select": (
            "Selecciona una o varias categorías con casillas:"
        ),
        "gui.help.rated": (
            "Enriquece los datos trimestrales con ratings de iconicidad y genera "
            "WordCount (con rating) y LemaCount (lemas colapsados). "
            "Requiere haber ejecutado el análisis de Types previamente."
        ),
        "gui.help.type_count": (
            "Elige si las gráficas deben usar las repeticiones reales o contar "
            "cada forma solo una vez. Esto solo afecta a las gráficas de Types; "
            "los JSON exportados siguen en formato estándar."
        ),
        "gui.empty.click_show_corpora": (
            "Pulsa 'Mostrar corpus inicializados' para cargar los corpus disponibles."
        ),
        "gui.empty.click_show_or_wait": (
            "Pulsa 'Mostrar corpus inicializados' o espera a que se carguen las categorías."
        ),
        "gui.empty.no_categories": "No hay categorías disponibles.",
        "gui.empty.no_corpora": "No hay corpus disponibles.",
        "gui.empty.processed_not_found": "No se encuentra la carpeta de corpus procesado.",
        "gui.status.ready": "Listo.",
        "gui.status.in_progress": "En curso...",
        "gui.error.title": "Error",
        "gui.error.talkbank_credentials": (
            "Introduce el email y la contraseña de TalkBank."
        ),
        "gui.error.set_processed_path": "Indica primero la ruta de corpus procesado.",
        "gui.error.select_category": (
            "Selecciona al menos una categoría o marca 'Todas las categorías'."
        ),
        "gui.error.corpus_download": "Error al descargar corpus",
        "gui.error.ratings_download": "Error al descargar ratings de iconicidad",
        "gui.error.init_corpus": "Error al inicializar corpus",
        "gui.error.analysis": "Error al ejecutar el análisis",
        "gui.info.in_progress": "En curso",
        "gui.notify.busy": "Ya hay otra tarea en curso.",
        "gui.log.download_corpora_start": "\nIniciando descarga de corpus de TalkBank...\n",
        "gui.log.download_complete": "\nDescarga completada.\n",
        "gui.log.ratings_download_start": "\nIniciando descarga de ratings de iconicidad...\n",
        "gui.log.ratings_download_complete": "\nDescarga de ratings completada.\n",
        "gui.log.iconicity_export_start": "\nLanzando exportación con iconicidad...\n",
        "gui.log.init_start": "\nIniciando inicialización de corpus...\n",
        "gui.log.init_complete": "\nInicialización completada.\n",
        "gui.log.analysis_start": "\nLanzando {action} para {corpora}...\n",
        "gui.log.iconicity_export_done": (
            "\nExportación con iconicidad completada. Resultados en: {path}\n"
        ),
        "gui.log.types_plots_done": "\nGeneración de gráficas de types completada.\n",
        "gui.log.types_plots_count_note": (
            "El criterio de conteo elegido solo se ha aplicado a las "
            "gráficas; los JSON exportados no cambian.\n"
        ),
        "gui.log.types_plots_saved": "Gráficas de types guardadas en: {path}\n",
        "gui.log.types_analysis_done": (
            "\nAnálisis de types completado. Resultados exportados en: {path}\n"
        ),
        "gui.log.token_plots_done": "\nGeneración de gráficas de tokens completada.\n",
        "gui.log.plots_saved_pair": "Gráficas guardadas en: {plots} y {distribution}\n",
        "gui.log.token_analysis_done": (
            "\nAnálisis de tokens completado. Resultados exportados en: {path}\n"
        ),
        "gui.log.corpora_refreshed": "Corpus inicializados en {path}: {list}\n",
        "gui.log.categories_load_error": "No se pudieron cargar las categorías: {error}",
        "gui.common.all_corpora": "todos los corpus",
        "gui.common.none": "(ninguno)",
        "gui.rated.data_found": "Datos encontrados en: {path}",
        "gui.rated.no_data": (
            "No se encuentran datos trimestrales. Ejecuta primero el análisis de Types."
        ),
        "gui.validation.set_processed_path": "Indica primero la ruta de corpus procesado.",
        "gui.validation.processed_name": (
            "La carpeta de corpus procesado debe llamarse {name}."
        ),
        "gui.validation.processed_missing": (
            "La carpeta de corpus procesado no existe: {path}"
        ),
        "gui.validation.no_corpora": (
            "No hay corpus procesados disponibles en {path}. "
            "Inicializa o refresca primero."
        ),
        "gui.validation.missing_corpora": (
            "Faltan corpus procesados para ejecutar el análisis: {list}"
        ),
        "gui.validation.quarterly_missing": (
            "La carpeta de datos trimestrales no existe: {path}"
        ),
        "gui.action.tokens_plot_generation": "generación de gráficas de tokens",
        "gui.action.types_plot_generation": "generación de gráficas de types",
        "gui.action.tokens_analysis": "análisis de tokens",
        "gui.action.types_analysis": "análisis de types",
        "gui.error.no_interpreter": (
            "No hay un interprete disponible con las dependencias necesarias "
            "para el análisis."
        ),
        "gui.error.external_exit": "El análisis externo terminó con código {code}.",
    },
}
