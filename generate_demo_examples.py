from pathlib import Path

from product_cards.export import export_card
from product_cards.generator import build_card
from product_cards.models import GeneratedText, ProductInput


BASE_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = BASE_DIR / "examples"
RESULTS_DIR = EXAMPLES_DIR / "results"

CASES = [
    ("dm02", "dm02"),
    ("test_temperature_sensor", "test_temperature_sensor"),
]


def main() -> int:
    for input_name, response_name in CASES:
        input_path = EXAMPLES_DIR / f"{input_name}.json"

        response_path = (
            EXAMPLES_DIR
            / "mock_responses"
            / f"{response_name}.json"
        )

        product = ProductInput.model_validate_json(
            input_path.read_text(encoding="utf-8")
        )

        generated = GeneratedText.model_validate_json(
            response_path.read_text(encoding="utf-8")
        )

        card = build_card(product, generated)

        json_output = RESULTS_DIR / f"{input_name}.json"
        markdown_output = RESULTS_DIR / f"{input_name}.md"

        export_card(card, json_output)
        export_card(card, markdown_output)

        print(f"Создана карточка: {product.name}")
        print(f"JSON: {json_output}")
        print(f"Markdown: {markdown_output}")
        print(f"Предупреждений: {len(card.validation_warnings)}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
