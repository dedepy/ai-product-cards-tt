from openai import OpenAI

from product_cards.models import (
    GeneratedText,
    ProductCard,
    ProductInput,
)
from product_cards.prompts import SYSTEM_PROMPT


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

    characteristics = {
        key: value if value is not None else "данных нет"
        for key, value in product.specs.items()
    }

    return ProductCard(
        **generated.model_dump(),
        characteristics=characteristics,
        missing_fields=product.missing_fields(),
    )
