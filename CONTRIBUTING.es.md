# Cómo contribuir a ChildConicity

[🇬🇧 English](CONTRIBUTING.md) | 🇪🇸 Español

Gracias por contribuir. ChildConicity es software de investigación citable: las aportaciones entran por `develop`, y `main` se queda como la línea publicada.

## Ramas

1. Parte de **`develop`**, no de `main`.
2. Crea una rama desde ahí (`fix/...`, `feat/...`, u otro nombre corto).
3. Abre un pull request **contra `develop`**.
4. Un maintainer revisa el PR. La CI tiene que pasar en Python 3.10, 3.11 y 3.12. Después mergeamos a `develop`.

No abras pull requests contra `main`. Los releases los mergean los maintainers de `develop` a `main`.

```bash
git clone https://github.com/ChildConicFoundation/ChildConicity.git
cd ChildConicity
git checkout develop
git pull
git checkout -b fix/descripcion-corta
```

Si trabajas desde un fork, parte igual de `develop` y abre el PR con base `develop`.

## Entorno y pruebas

Sigue el [README](README.es.md) para instalar. Después:

```bash
source .venv/bin/activate
pip install -e ".[dev]"
./run_tests.sh
```

La CI corre en cada push a una rama y en los pull requests. En local, mantén la cobertura en **el 80% o más**.

No subas corpus, ratings de iconicidad, gráficas generadas ni ficheros `*_result.json`. Eso se queda en local.

## Qué enviar

Encajan bien las correcciones, los tests, la documentación y los normalizadores de corpus nuevos o mejorados.

Abre un issue antes si el cambio es grande o altera resultados de análisis. No subas la versión del paquete, no edites metadatos de release y no crees tags; los releases los hacen los maintainers.

## Licencia

Al contribuir, aceptas que tu trabajo quede bajo la [Boost Software License 1.0](LICENSE).
