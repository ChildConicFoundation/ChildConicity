import argparse
from dataclasses import dataclass
from typing import List, Optional


DEFAULT_OUTPUT_DIR = "quarterly_grammatical_categories"


@dataclass(frozen=True)
class GrammaticalCLIOptions:
    categories: Optional[List[str]]
    list_categories: bool = False
    output_dir: str = DEFAULT_OUTPUT_DIR

    @classmethod
    def from_namespace(cls, namespace):
        return cls(
            categories=cls._normalize_categories(namespace.categories),
            list_categories=namespace.list_categories,
            output_dir=namespace.output_dir,
        )

    @staticmethod
    def _normalize_categories(raw_categories):
        if raw_categories is None:
            return None

        if isinstance(raw_categories, str):
            raw_categories = [raw_categories]

        categories = []
        seen_categories = set()

        for raw_value in raw_categories:
            for category in raw_value.split(","):
                normalized_category = category.strip().casefold()
                if not normalized_category or normalized_category in seen_categories:
                    continue
                seen_categories.add(normalized_category)
                categories.append(normalized_category)

        if not categories or categories == ["all"]:
            return None

        if "all" in categories:
            raise ValueError(
                "Use 'all' on its own or a specific category list, but not both."
            )

        return categories

    def validate_against(self, available_categories):
        if self.categories is None:
            return self

        available_lookup = {
            category.casefold(): category for category in available_categories
        }
        missing_categories = [
            category for category in self.categories if category not in available_lookup
        ]

        if missing_categories:
            available_categories_text = ", ".join(available_categories)
            missing_categories_text = ", ".join(missing_categories)
            raise ValueError(
                "The following categories do not exist in the corpus: "
                f"{missing_categories_text}. "
                f"Available categories: {available_categories_text}"
            )

        return GrammaticalCLIOptions(
            categories=[available_lookup[category] for category in self.categories],
            list_categories=self.list_categories,
            output_dir=self.output_dir,
        )


def build_grammatical_options_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Process the corpus by types and filter by grammatical categories."
        )
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=["all"],
        help=(
            "Use 'all' to include all categories, or a list such as "
            "'--categories noun verb' o '--categories noun,verb'."
        ),
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="List available grammatical categories and exit.",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where results will be exported.",
    )
    return parser


def parse_grammatical_cli_options(argv=None):
    parser = build_grammatical_options_parser()
    namespace = parser.parse_args(argv)
    return GrammaticalCLIOptions.from_namespace(namespace)
