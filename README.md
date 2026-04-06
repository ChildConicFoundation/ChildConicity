# ChildConicity

[![Python Tests](https://github.com/TU_USUARIO/ChildConicity/actions/workflows/python-tests.yml/badge.svg)](https://github.com/TU_USUARIO/ChildConicity/actions/workflows/python-tests.yml)

## Ejecución de Pruebas

### Ejecución Local

Para ejecutar las pruebas y generar el informe de cobertura localmente:

1. Asegúrate de tener todas las dependencias instaladas:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el script de pruebas:
   ```bash
   ./run_tests.sh
   ```

El script:
- Ejecutará todas las pruebas
- Generará un informe de cobertura HTML
- Verificará que la cobertura sea mayor al 80%
- Guardará el informe en el directorio `coverage_report/`

Para ver el informe de cobertura, abre el archivo `coverage_report/htmlcov/index.html` en tu navegador.

### Pipeline de GitHub Actions

La cobertura de código se genera automáticamente en cada ejecución del pipeline. Puedes encontrar el informe detallado en los artefactos de la última ejecución de GitHub Actions.

Para ver el informe de cobertura:
1. Ve a la pestaña "Actions" en GitHub
2. Selecciona la última ejecución exitosa
3. Descarga el artefacto "coverage-report"
4. Abre el archivo `htmlcov/index.html` en tu navegador

## Ejecución del Programa Principal

El programa principal se encuentra en `examples/main2.py` y realiza un análisis completo de la iconicidad en el desarrollo del lenguaje infantil. Para ejecutarlo:

1. Asegúrate de tener todas las dependencias instaladas:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el programa principal:
   ```bash
   python3 examples/main2.py
   ```

### ¿Qué hace el programa?

El programa realiza las siguientes operaciones:

1. **Inicialización de Corpus**:
   - Requiere que todos los corpus (Brent, NewEngland, Post, Bloom, Brown, HSLLD, Kuczaj, Sachs y VanKleeck) estén ubicados dentro de la carpeta `Corpus/` en la raíz del proyecto
   - La estructura de directorios debe ser:
     ```
     Corpus/
     ├── Brent/
     ├── Bloom/
     ├── Brown/
     ├── HSLLD/
     ├── Kuczaj/
     ├── NewEngland/
     ├── Post/
     ├── Sachs/
     └── VanKleeck/
     ```
   - Procesa los corpus y los organiza en una nueva estructura en `Corpus_modified/`
   - Prepara los datos para su análisis

2. **Análisis de Datos**:
   - Agrupa los datos por edad en trimestres (formato YYQ)
   - Separa las expresiones de niños y adultos
   - Analiza la iconicidad de las palabras utilizadas
   - Genera estadísticas detalladas por grupo de edad

3. **Generación de Gráficos**:
   - Crea gráficos de distribución de iconicidad por grupo de edad
   - Genera gráficos comparativos de palabras icónicas vs no icónicas
   - Produce visualizaciones separadas para adultos y niños
   - Los gráficos se guardan en:
     - `iconic_vs_noniconic/`: Gráficos de comparación general
     - `pruebas/`: Gráficos de distribución de iconicidad

### Resultados Esperados

Al ejecutar el programa, obtendrás:

1. **Estadísticas por Grupo de Edad**:
   - Total de palabras utilizadas
   - Distribución de palabras icónicas vs no icónicas
   - Top 10 palabras más usadas en cada categoría
   - Porcentajes de iconicidad para adultos y niños

2. **Gráficos de Análisis**:
   - Distribución de iconicidad por grupo de edad
   - Comparativas de uso de palabras icónicas vs no icónicas
   - Análisis separado para adultos y niños
   - Visualización de tendencias en el desarrollo del lenguaje

3. **Metadatos y Estructura**:
   - Información detallada de los archivos procesados
   - Estructura del corpus organizado
   - Ejemplos de expresiones tempranas

### Notas Importantes

- El programa procesa una gran cantidad de datos, por lo que la ejecución puede tomar varios minutos
- Se generan múltiples archivos de salida en diferentes directorios
- Los resultados incluyen tanto análisis cuantitativos como visualizaciones gráficas
- Los datos se agrupan en trimestres para facilitar el análisis del desarrollo lingüístico
