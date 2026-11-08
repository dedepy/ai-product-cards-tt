from pathlib import Path

import pytest

from product_cards.generator import build_card
from product_cards.models import GeneratedText, ProductInput


EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"


@pytest.mark.parametrize(
    "name",
    ["dm02", "test_temperature_sensor"],
)
def test_demo_example(name):
    product_path = EXAMPLES_DIR / f"{name}.json"

    response_path = (
        EXAMPLES_DIR / "mock_responses" / f"{name}.json"
    )

    product = ProductInput.model_validate_json(
        product_path.read_text(encoding="utf-8")
    )

    generated = GeneratedText.model_validate_json(
        response_path.read_text(encoding="utf-8")
    )

    card = build_card(product, generated)

    assert card.seo_title
    assert 3 <= len(card.search_queries) <= 5

    for key, value in product.specs.items():
        assert card.characteristics[key] == (
            value if value is not None else "данных нет"
        )

    assert card.validation_warnings
