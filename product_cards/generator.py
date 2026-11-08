
from openai import OpenAI

from product_cards.models import (
    GeneratedText,
    ProductCard,
    ProductInput,
)
from product_cards.prompts import SYSTEM_PROMPT
from product_cards.quality import validate_generated_text


def generate_card(
    product: ProductInput,
    client: OpenAI,
    model: str,
) -> ProductCard:
    product_json = product.model_dump_json(indent=2)

    response = client.responses.parse(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=(
            "Подготовь карточку товара на основе "
            "следующих данных:\n\n"
            f"{product_json}"
        ),
        text_format=GeneratedText,
        store=False,
    )

    generated = response.output_parsed

    if generated is None:
        raise RuntimeError(
            "LLM не вернула структурированный результат"
        )

    # Проверяем качество сгенерированного текста
    warnings = validate_generated_text(generated)

    # Берём характеристики только из входных данных
    characteristics = {
        key: value if value is not None else "данных нет"
        for key, value in product.specs.items()
    }

    # Формируем итоговую карточку товара
    return ProductCard(
        **generated.model_dump(),
        characteristics=characteristics,
        missing_fields=product.missing_fields(),
        validation_warnings=warnings,
    )
