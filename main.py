import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    OpenAI,
)
from pydantic import ValidationError

from product_cards.generator import generate_card
from product_cards.models import ProductInput
from product_cards.export import export_card


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Product Card Generator"
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Путь к JSON-файлу товара",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Проверить JSON без обращения к LLM",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Путь сохранения карточки (.json или .md)",
    )


    args = parser.parse_args()

    try:
        content = args.file.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"Ошибка чтения файла: {exc}",
            file=sys.stderr,
        )
        return 1

    try:
        product = ProductInput.model_validate_json(content)
    except ValidationError as exc:
        print(
            f"Ошибка входных данных:\n{exc}",
            file=sys.stderr,
        )
        return 1

    if args.validate_only:
        print("Данные успешно проверены.")
        print(product.model_dump_json(indent=2))
        print("Требуют уточнения:", product.missing_fields())
        return 0

    if args.output is not None:
        allowed_extensions = {".json", ".md"}

        if args.output.suffix.lower() not in allowed_extensions:
            print(
                "Ошибка: поддерживаются только .json и .md",
                file=sys.stderr,
            )
            return 1

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()

    if not api_key or api_key == "your_api_key_here":
        print(
            "OPENAI_API_KEY не настроен в .env",
            file=sys.stderr,
        )
        return 1

    try:
        client = OpenAI(
            api_key=api_key,
            timeout=45.0,
            max_retries=2,
        )

        card = generate_card(
            product=product,
            client=client,
            model=model,
        )



    except APIStatusError as exc:

        try:

            payload = exc.response.json()

        except ValueError:

            payload = {}

        error = payload.get("error", {})

        if not isinstance(error, dict):
            error = {}

        code = error.get("code", "unknown")

        error_type = error.get("type", "unknown")

        message = error.get("message", "Нет описания")

        print(f"HTTP: {exc.status_code}", file=sys.stderr)

        print(f"Code: {code}", file=sys.stderr)

        print(f"Type: {error_type}", file=sys.stderr)

        print(f"Message: {message}", file=sys.stderr)

        return 1


    except APIConnectionError:
        print(
            "Не удалось подключиться к LLM API",
            file=sys.stderr,
        )
        return 1

    except APIError:
        print(
            "Ошибка при обращении к LLM API",
            file=sys.stderr,
        )
        return 1

    except (RuntimeError, ValidationError) as exc:
        print(
            f"Ошибка обработки ответа LLM: {exc}",
            file=sys.stderr,
        )
        return 1


    if args.output is not None:
        try:
            export_card(card, args.output)
        except (OSError, ValueError) as exc:
            print(
                f"Ошибка сохранения: {exc}",
                file=sys.stderr,
            )
            return 1

        print(f"Карточка сохранена: {args.output}")

    else:
        print(card.model_dump_json(indent=2))

    return 0



if __name__ == "__main__":
    raise SystemExit(main())
