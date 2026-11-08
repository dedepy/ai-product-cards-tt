import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from product_cards.models import ProductInput


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Product Card Generator"
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Путь к JSON-файлу с данными товара",
    )

    args = parser.parse_args()

    try:
        content = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Ошибка чтения файла: {exc}", file=sys.stderr)
        return 1

    try:
        product = ProductInput.model_validate_json(content)
    except ValidationError as exc:
        print(f"Ошибка входных данных:\n{exc}", file=sys.stderr)
        return 1

    print("Данные успешно проверены.")
    print(product.model_dump_json(indent=2))

    missing = product.missing_fields()

    if missing:
        print("\nТребуют уточнения:")
        for field in missing:
            print(f"- {field}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
