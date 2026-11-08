import pytest

from product_cards.models import GeneratedText
from product_cards.quality import (
    CardQualityError,
    validate_generated_text,
)


def make_generated_text(**changes) -> GeneratedText:
    data = {
        "seo_title": "Манометр DM 02",
        "seo_description": "А" * 900,
        "search_queries": [
            "манометр DM 02",
            "манометр показывающий",
            "манометр Манотомь",
        ],
        "commercial_text": "Прибор для измерения давления",
    }

    data.update(changes)
    return GeneratedText(**data)


@pytest.mark.parametrize("length", [800, 1200])
def test_valid_description_boundaries(length):
    generated = make_generated_text(
        seo_description="А" * length
    )

    assert validate_generated_text(generated) == []


def test_valid_title_boundary():
    generated = make_generated_text(
        seo_title="М" * 70
    )

    assert validate_generated_text(generated) == []


def test_short_description_warning():
    generated = make_generated_text(
        seo_description="Краткое описание"
    )

    warnings = validate_generated_text(generated)

    assert len(warnings) == 1
    assert "SEO-описание" in warnings[0]


@pytest.mark.parametrize(
    "changes, expected_error",
    [
        (
            {"seo_title": "М" * 71},
            "SEO-заголовок",
        ),
        (
            {"seo_description": "А" * 1201},
            "SEO-описание",
        ),
        (
            {"search_queries": ["манометр", "датчик"]},
            "Поисковых запросов",
        ),
        (
            {
                "search_queries": [
                    "Манометр",
                    "манометр",
                    "датчик",
                ]
            },
            "повторяющиеся",
        ),
        (
            {"commercial_text": "   "},
            "Коммерческий блок",
        ),
        (
            {"seo_title": "   "},
            "SEO-заголовок",
        ),
    ],
)
def test_invalid_generated_content(changes, expected_error):
    generated = make_generated_text(**changes)

    with pytest.raises(
        CardQualityError,
        match=expected_error,
    ):
        validate_generated_text(generated)
