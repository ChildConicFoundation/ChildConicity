# ChildConicity

[![CI](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/ChildConicFoundation/ChildConicity/actions/workflows/python-tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-≥80%25-04e762?logo=pytest&logoColor=white)](https://github.com/ChildConicFoundation/ChildConicity#pruebas)
[![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: BSL-1.0](https://img.shields.io/badge/License-BSL--1.0-0052CC)](LICENSE)

[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-555)](#instalación)
[![Corpus](https://img.shields.io/badge/corpus-CHILDES%20%2F%20TalkBank-8B4513)](https://talkbank.org/childes/)
[![Iconicity ratings](https://img.shields.io/badge/iconicity-OSF-orange)](https://osf.io/ex37k/)
[![GUI](https://img.shields.io/badge/interfaz-Tkinter%20GUI-FF6F00)](#uso-recomendado-interfaz-gráfica)
[![CLI](https://img.shields.io/badge/automatización-CLI%20%7C%20agentes-2ea44f)](#automatización-e-integración-con-agentes-de-ia)
[![Languages](https://img.shields.io/badge/idiomas-en%20%7C%20es-007ec6)](README.es.md)
[![Last commit](https://img.shields.io/github/last-commit/ChildConicFoundation/ChildConicity)](https://github.com/ChildConicFoundation/ChildConicity/commits/main)
[![Issues](https://img.shields.io/github/issues/ChildConicFoundation/ChildConicity)](https://github.com/ChildConicFoundation/ChildConicity/issues)

[🇬🇧 English](README.md) | 🇪🇸 Español

ChildConicity permite procesar corpus CHILDES/TalkBank y analizar la iconicidad en el desarrollo del lenguaje infantil. El programa normaliza transcripciones `.cha`, agrupa los datos por edad en trimestres y genera resultados por tokens, categorías gramaticales y ratings de iconicidad.

## Instalación

Se recomienda usar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# o: pip install -e ".[dev]"   # instalación editable con dependencias de test
```

Para descargar corpus desde TalkBank necesitas una cuenta de TalkBank y tener Chrome/Chromedriver disponible, porque la autenticación se hace con Selenium.

Antes de ejecutar cualquier análisis, también necesitas la base de datos de ratings de iconicidad en `iconicity_ratings/iconicity_ratings_cleaned.csv`. No viene incluida en el repositorio. Descárgala desde la GUI (**Descargar ratings de iconicidad**) o desde terminal con `python3 -m src.cli.download_iconicity_ratings` (se obtiene desde OSF; no requiere cuenta).

## Uso recomendado: interfaz gráfica

La forma más sencilla de usar el programa es la GUI:

```bash
source .venv/bin/activate
python3 examples/gui.py
```

En la ventana principal:

0. Elige **Idioma** (`English` / `Español`) arriba. La preferencia se guarda en `.childconicity_locale` (o usa `CHILDCONICITY_LOCALE=en|es`).
1. En la sección **Descargas**, obtén los datos que necesites:
   - **Download corpora**: requiere email y contraseña de TalkBank; se guardan en `Corpora/`.
   - **Descargar ratings de iconicidad**: descarga la base de datos de iconicidad desde OSF a `iconicity_ratings/iconicity_ratings_cleaned.csv` (necesaria para todos los análisis).
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

En scripts y agentes, conviene usar variables de entorno para que las credenciales no queden en el historial del shell:

```bash
export CHILDCONICITY_TALKBANK_USER=tu@email
export CHILDCONICITY_TALKBANK_PASSWORD=tu_password
python3 -m src.cli.download_corpora --corpora Brent Bloom
```

Los flags de CLI tienen prioridad sobre las variables de entorno si se usan ambos.

Opciones útiles:

- `--user EMAIL`: email de TalkBank. Por defecto usa `CHILDCONICITY_TALKBANK_USER`.
- `--password PASSWORD`: contraseña de TalkBank. Por defecto usa `CHILDCONICITY_TALKBANK_PASSWORD`.
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
- `--url URL`: cambia la URL de descarga en OSF.
- `--force`: sobrescribe el CSV si ya existe.

### Inicializar corpus

```bash
source .venv/bin/activate
python3 examples/initialize_corpuses.py
python3 examples/initialize_corpuses.py --source-root Corpora --output-root Corpora_modified
```

Por defecto lee desde `Corpora/` y escribe en `Corpora_modified/`.

Opciones útiles:

- `--source-root DIR`: carpeta con corpus originales.
- `--output-root DIR`: carpeta con corpus normalizados.

Los normalizadores incluidos procesan estos corpus: `Bates`, `Bloom`, `Brent`, `Brown`, `HSLLD`, `Kuczaj`, `NewEngland`, `Post`, `Providence`, `Sachs` y `VanKleeck`.

### Ejecutar análisis

El runner de análisis es el mismo punto de entrada que usa la GUI en un subproceso:

```bash
source .venv/bin/activate
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories
```

Modos:

- `tokens`: conteo de palabras icónicas y no icónicas por trimestre.
- `types`: exportación por categorías gramaticales. Es obligatorio antes de `rated`.
- `rated`: enriquece la salida de `types` con ratings de iconicidad (`WordCount` con ratings y `LemaCount`).

Opciones útiles:

- `--corpus NOMBRE`: filtra por corpus; puede repetirse.
- `--category CATEGORIA`: filtra categorías gramaticales en modo `types`; puede repetirse.
- `--output-dir DIR`: cambia la carpeta de salida.
- `--iconicity-csv FILE`: usa otro CSV de ratings.
- `--generate-plots`: genera visualizaciones PNG.
- `--plots-dir DIR`: carpeta de gráficas de tokens o types (modos `tokens` y `types`).
- `--distribution-dir DIR`: gráficas de distribución acumulada en modo `tokens`.
- `--plot-count-criteria GRUPO`: grupos de hablantes para gráficas de types (`adults`, `children`, ...); puede repetirse.
- `--result-file FILE`: escribe un JSON resumen legible por máquina (ver más abajo).
- `--type-count-mode with_repetitions|only_once`: cambia cómo se cuentan los types en las gráficas.

Archivos resumen por defecto si no se indica `--result-file`: `tokens_result.json`, `types_result.json` y `rated_result.json` en la raíz del proyecto. Son artefactos de ejecución y git los ignora (`*_result.json`).

Ejemplos:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --corpus Brent --corpus Post
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --category noun --category verb --generate-plots
python3 src/gui_analysis_runner.py rated --processed-root quarterly_grammatical_categories --output-dir rated_quarterly_grammatical_categories
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --generate-plots \
  --plots-dir quarterly_valid_words/iconic_vs_noniconic \
  --distribution-dir quarterly_valid_words/distribution \
  --result-file /tmp/tokens_result.json
```

#### JSON resumen del runner

Al terminar, el runner escribe un JSON con las rutas generadas. Es el contrato principal para scripts y agentes:

```json
{
  "outputs": { "...": "..." },
  "plot_outputs": { "...": "..." }
}
```

- `outputs`: rutas exportadas por el análisis. En modos `tokens` y `types` es un mapa anidado de JSON/CSV generados. En modo `rated` contiene `source_dir` y `output_dir`.
- `plot_outputs`: solo aparece con `--generate-plots`. Incluye `plots_dir`, opcionalmente `distribution_dir`, y un mapa `files` con las rutas PNG.

La GUI usa el mismo runner con un `--result-file` temporal y luego lee ese JSON para mostrar los archivos generados.

## Automatización e integración con agentes de IA

Para scripts, jobs de CI o agentes de IA, conviene usar la línea de comandos en lugar de la GUI Tkinter. La GUI no añade lógica de análisis: lanza `src/gui_analysis_runner.py` en un subproceso con los mismos servicios documentados arriba.

### Pipeline recomendado

Ejecuta estos pasos desde la raíz del proyecto con el entorno virtual activado:

```bash
python3 -m src.cli.download_iconicity_ratings
python3 examples/initialize_corpuses.py --source-root Corpora --output-root Corpora_modified
python3 src/gui_analysis_runner.py types --processed-root Corpora_modified --result-file /tmp/types_result.json
python3 src/gui_analysis_runner.py rated \
  --processed-root quarterly_grammatical_categories \
  --output-dir rated_quarterly_grammatical_categories \
  --result-file /tmp/rated_result.json
```

Análisis de tokens opcional:

```bash
python3 src/gui_analysis_runner.py tokens --processed-root Corpora_modified --result-file /tmp/tokens_result.json
```

### Por qué la CLI encaja bien con agentes

- **Pasos composables**: cada comando tiene una responsabilidad y entradas/salidas claras.
- **Paridad con la GUI**: los agentes obtienen el mismo comportamiento que la interfaz gráfica.
- **Datos estructurados al finalizar**: usa `--result-file` y parsea el JSON en lugar de adivinar rutas de salida.
- **Ejecuciones acotadas**: `--corpus` y `--category` reducen el tiempo en iteraciones.
- **Descargas idempotentes**: ratings y corpus se omiten si ya existen, salvo con `--force`.
- **Headless por defecto**: todos los análisis corren sin pantalla. Solo la descarga de corpus TalkBank requiere Chrome/Selenium.

### Precondiciones que un agente debe comprobar

1. Existe `iconicity_ratings/iconicity_ratings_cleaned.csv`.
2. Existe `Corpora_modified/` con los corpus a analizar.
3. Para `rated`, debe existir `quarterly_grammatical_categories/` de una ejecución previa de `types`.
4. Para gráficas, deben estar instalados `matplotlib`, `numpy` y `seaborn` (ya figuran en `requirements.txt`).

### Seguridad y notas operativas

- Usa `CHILDCONICITY_TALKBANK_USER` y `CHILDCONICITY_TALKBANK_PASSWORD` para las credenciales de TalkBank en lugar de `--user` / `--password` en la línea de comandos.
- La descarga de TalkBank es el paso más frágil para automatización porque depende de Selenium y de una sesión real de navegador.
- Las ejecuciones largas solo reportan progreso por stdout; aún no hay API de progreso en streaming.
- Los ficheros `*_result.json` son artefactos locales. No los trates como entradas del proyecto ni los subas a git.

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
- Los JSON resumen del runner (`*_result.json`) se generan localmente y git los ignora.
- Las gráficas de types se guardan en subcarpetas dentro del directorio de salida elegido, por ejemplo `plots_count_criteria_all/`.
- En modo `tokens`, si no pasas `--plots-dir` y `--distribution-dir`, las gráficas se escriben en `iconic_vs_noniconic/` y `distribution/` en la raíz del proyecto. La GUI, en cambio, las coloca dentro del directorio de salida seleccionado.
