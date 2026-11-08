
import json

import pytest

from product_cards.export import (
    card_to_markdown,
    export_card,
)
from product_cards.models import ProductCard


@pytest.fixture
def sample_card():
    return ProductCard(
        seo_title="Манометр DM 02",
        seo_description="Тестовое описание",
        search_queries=[
            "манометр DM 02",
            "манометр показывающий",
            "манометр Манотомь",
        ],
        commercial_text="Прибор для измерения давления",
        characteristics={
            "класс точности": "1,5",
            "диапазон измерений": "данных нет",
        },
        missing_fields=["specs.диапазон измерений"],
        validation_warnings=["Описание слишком короткое"],
    )


def test_markdown_contains_required_sections(sample_card):
    result = card_to_markdown(sample_card)

    assert "# Манометр DM 02" in result
    assert "## SEO-описание" in result
    assert "## Характеристики" in result
    assert "## Поисковые запросы" in result
    assert "## Коммерческий блок" in result
    assert "## Предупреждения" in result


def test_export_json(sample_card, tmp_path):
    output = tmp_path / "card.json"

    export_card(sample_card, output)

    data = json.loads(
        output.read_text(encoding="utf-8")
    )

    assert data["seo_title"] == "Манометр DM 02"
    assert data["characteristics"]["класс точности"] == "1,5"


def test_export_markdown(sample_card, tmp_path):
    output = tmp_path / "card.md"

    export_card(sample_card, output)

    content = output.read_text(encoding="utf-8")

    assert "# Манометр DM 02" in content
    assert "Описание слишком короткое" in content


def test_export_creates_directory(sample_card, tmp_path):
    output = tmp_path / "results" / "card.json"

    export_card(sample_card, output)

    assert output.exists()


def test_unsupported_format(sample_card, tmp_path):
    output = tmp_path / "card.txt"

    with pytest.raises(
        ValueError,
        match="Неподдерживаемый формат",
    ):
        export_card(sample_card, output)
