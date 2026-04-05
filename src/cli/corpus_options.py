import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class CorpusCLIOptions:
    corpora: Optional[List[str]]
    list_corpora: bool = False

    @classmethod
    def from_namespace(cls, namespace):
        return cls(
            corpora=cls._normalize_corpora(namespace.corpora),
            list_corpora=namespace.list_corpora,
        )

    @staticmethod
    def _normalize_corpora(raw_corpora):
        if raw_corpora is None:
            return None

        if isinstance(raw_corpora, str):
            raw_corpora = [raw_corpora]

        corpora = []
        seen_corpora = set()

        for raw_value in raw_corpora:
            for corpus_name in raw_value.split(","):
                normalized_name = corpus_name.strip().casefold()
                if not normalized_name or normalized_name in seen_corpora:
                    continue
                seen_corpora.add(normalized_name)
                corpora.append(normalized_name)

        if not corpora or corpora == ["all"]:
            return None

        if "all" in corpora:
            raise ValueError(
                "Usa 'all' por separado o una lista concreta de corpus, pero no ambos."
            )

        return corpora

    def validate_against(self, available_corpora):
        if self.corpora is None:
            return self

        available_lookup = {
            corpus_name.casefold(): corpus_name for corpus_name in available_corpora
        }
        missing_corpora = [
            corpus_name
            for corpus_name in self.corpora
            if corpus_name not in available_lookup
        ]

        if missing_corpora:
            available_corpora_text = ", ".join(available_corpora)
            missing_corpora_text = ", ".join(missing_corpora)
            raise ValueError(
                "Los siguientes corpus no existen en Corpus_modified: "
                f"{missing_corpora_text}. "
                f"Corpus disponibles: {available_corpora_text}"
            )

        return CorpusCLIOptions(
            corpora=[available_lookup[corpus_name] for corpus_name in self.corpora],
            list_corpora=self.list_corpora,
        )


def add_corpus_options(parser):
    parser.add_argument(
        "--corpora",
        nargs="+",
        default=["all"],
        help=(
            "Usa 'all' para incluir todos los corpus, o una lista como "
            "'--corpora Brent Post' o '--corpora Brent,Post'."
        ),
    )
    parser.add_argument(
        "--list-corpora",
        action="store_true",
        help="Muestra los corpus disponibles en Corpus_modified y termina.",
    )
    return parser


def build_corpus_options_parser(
    description="Procesa el corpus y permite filtrar qué corpus usar."
):
    parser = argparse.ArgumentParser(description=description)
    return add_corpus_options(parser)


def parse_corpus_cli_options(argv=None):
    parser = build_corpus_options_parser()
    namespace = parser.parse_args(argv)
    return CorpusCLIOptions.from_namespace(namespace)
