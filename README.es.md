# ChildConicity

[![Python Tests](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml)

[🇬🇧 English](README.md) | 🇪🇸 Español

ChildConicity permite procesar corpus CHILDES/TalkBank y analizar la iconicidad en el desarrollo del lenguaje infantil. El programa normaliza transcripciones `.cha`, agrupa los datos por edad en trimestres y genera resultados por tokens, categorías gramaticales y ratings de iconicidad.

## Instalación

Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para descargar corpus desde TalkBank necesitas una cuenta de TalkBank y tener Chrome/Chromedriver disponible, porque la autenticación se hace con Selenium.

## Uso recomendado: interfaz gráfica

La forma más sencilla de usar el programa es la GUI:

```bash
source .venv/bin/activate
python3 examples/gui.py
```

En la ventana principal:

0. Elige **Idioma** (`English` / `Español`) arriba. La preferencia se guarda en `.childconicity_locale` (o usa `CHILDCONICITY_LOCALE=en|es`).
1. Si todavía no tienes corpus locales, introduce tu email y contraseña de TalkBank y pulsa `Download corpora`. Por defecto se descargan en `Corpora/`.
2. Revisa las rutas:
   - `Source corpus`: carpeta con corpus originales, normalmente `Corpora/`.
   - `Processed corpus`: carpeta de salida normalizada, normalmente `Corpora_modified/`.
3. Pulsa `Initialize corpora` para transformar los corpus originales al formato que usan los análisis.
4. Pulsa `Show initialized corpora` para cargar la lista de corpus disponibles.
5. Selecciona `All corpora` o marca corpus concretos.
6. Elige el modo:
   - `Tokens`: análisis de palabras icónicas y no icónicas por trimestre.
   - `Types`: análisis por categorías gramaticales.
7. Pulsa `Run analysis` para exportar datos o `Generate plots` para crear las visualizaciones.
8. Para `Rated`, primero ejecuta `Types`; después usa la sección de exportación con iconicidad para generar `WordCount` con ratings y `LemaCount`.

Directorios de salida por defecto:

- `quarterly_valid_words/`: resultados del análisis de tokens.
- `quarterly_grammatical_categories/`: resultados del análisis de types.
- `rated_quarterly_grammatical_categories/`: resultados enriquecidos con ratings de iconicidad.
- `iconic_vs_noniconic/` y `distribution/`: gráficas de tokens cuando se generan desde línea de comandos sin personalizar rutas.
- En la GUI, las gráficas de tokens se guardan dentro del directorio de salida elegido, en `iconic_vs_noniconic/` y `distribution/`.

## Uso por línea de comandos

La GUI llama internamente a los mismos servicios que se pueden ejecutar desde terminal.

### Descargar corpus

```bash
source .venv/bin/activate
python3 -m src.cli.download_corpora --user tu@email --password tu_password --corpora Brent Bloom
```

Opciones útiles:

- `--corpora Brent Bloom`: descarga solo esos corpus. Si se omite, intenta descargar todos.
- `--output-dir Corpora`: cambia la carpeta de destino.
- `--force`: sobrescribe corpus ya existentes.
- `--no-headless`: muestra el navegador durante el login.

### Descargar ratings de iconicidad

Los análisis de iconicidad usan `iconicity_ratings/iconicity_ratings_cleaned.csv`.
Si no lo tienes, o quieres volver a descargarlo desde OSF:

```bash
source .venv/bin/activate
python3 -m src.cli.download_iconicity_ratings
```

Opciones útiles:

- `--output FILE`: cambia la ruta de destino.
- `--force`: sobrescribe el CSV si ya existe.

### Inicializar corpus

```bash
source .venv/bin/activate
python3 examples/initialize_corpuses.py
```

Por defecto lee desde `Corpora/` y escribe en `Corpora_modified/`.

Los normalizadores incluidos procesan estos corpus: `Bates`, `Bloom`, `Brent`, `Brown`, `HSLLD`, `Kuczaj`, `NewEngland`, `Post`, `Providence`, `Sachs` y `VanKleeck`.

### Ejecutar análisis

El runner de análisis es:

```bash
source .venv/bin/activate
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories
```

Opciones útiles:

- `--corpus NOMBRE`: filtra por corpus; puede repetirse.
- `--category CATEGORIA`: filtra categorías gramaticales en modo `types`; puede repetirse.
- `--output-dir DIR`: cambia la carpeta de salida.
- `--iconicity-csv FILE`: usa otro CSV de ratings.
- `--result-file FILE`: cambia el JSON resumen del runner.
- `--type-count-mode with_repetitions|only_once`: cambia cómo se cuentan los types en las gráficas.

Ejemplos:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --corpus Brent --corpus Post
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --category noun --category verb --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories --output-dir rated_quarterly_grammatical_categories
```

## ¿Qué hace el análisis?

El programa:

1. Lee corpus normalizados desde `Corpora_modified/`.
2. Agrupa los datos por edad en trimestres.
3. Separa producciones de adultos, niños y, cuando aplica, otros niños.
4. Cruza las palabras o lemas con `iconicity_ratings/iconicity_ratings_cleaned.csv`.
5. Exporta JSON/CSV con estadísticas por trimestre.
6. Genera gráficas de distribución de iconicidad cuando se solicita.

## Pruebas

Para ejecutar las pruebas y generar el informe de cobertura:

```bash
source .venv/bin/activate
./run_tests.sh
```

El script:

- Ejecuta todas las pruebas.
- Genera un informe de cobertura HTML.
- Verifica que la cobertura sea mayor al 80%.
- Guarda el informe en `coverage_report/htmlcov/`.

El pipeline de GitHub Actions ejecuta las pruebas y publica el artefacto `coverage-report` con el informe de cobertura.

## Notas importantes

- `iconicity_ratings/iconicity_ratings_cleaned.csv` se puede descargar desde la GUI o con `python3 -m src.cli.download_iconicity_ratings`.
- La ejecución puede tardar varios minutos si se procesan muchos corpus.
- Se generan múltiples archivos de salida en JSON, CSV y PNG.
- Los nombres actuales de carpetas son `Corpora/` y `Corpora_modified/`.
