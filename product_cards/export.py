from pathlib import Path

from product_cards.models import ProductCard


def card_to_markdown(card: ProductCard) -> str:
    lines = [
        f"# {card.seo_title}",
        "",
        "## SEO-описание",
        "",
        card.seo_description,
        "",
        "## Характеристики",
        "",
    ]

    if card.characteristics:
        for name, value in card.characteristics.items():
            lines.append(f"- **{name}:** {value}")
    else:
        lines.append("Данных нет")

    lines.extend([
        "",
        "## Поисковые запросы",
        "",
    ])

    for query in card.search_queries:
        lines.append(f"- {query}")

    lines.extend([
        "",
        "## Коммерческий блок",
        "",
        card.commercial_text,
        "",
        "## Данные, требующие уточнения",
        "",
    ])

    if card.missing_fields:
        for field in card.missing_fields:
            lines.append(f"- {field}")
    else:
        lines.append("Нет")

    lines.extend([
        "",
        "## Предупреждения",
        "",
    ])

    if card.validation_warnings:
        for warning in card.validation_warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("Нет")

    return "\n".join(lines) + "\n"


def export_card(
    card: ProductCard,
    output_path: Path,
) -> None:
    extension = output_path.suffix.lower()

    if extension == ".json":
        content = card.model_dump_json(indent=2)

    elif extension == ".md":
        content = card_to_markdown(card)

    else:
        raise ValueError(
            "Неподдерживаемый формат. "
            "Используйте .json или .md"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        content,
        encoding="utf-8",
    )
