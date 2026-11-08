import pytest
from pydantic import ValidationError

from product_cards.models import ProductInput


def test_valid_product():
    product = ProductInput(
        name="  Манометр DM 02  ",
        manufacturer="  Манотомь  ",
        specs={
            " диапазон измерений ": " 0–1,6 МПа "
        },
        description="Измеряет давление",
    )

    assert product.name == "Манометр DM 02"
    assert product.manufacturer == "Манотомь"
    assert product.specs == {
        "диапазон измерений": "0–1,6 МПа"
    }
    assert product.missing_fields() == []


def test_missing_optional_fields():
    product = ProductInput(name="Манометр")

    assert product.missing_fields() == [
        "manufacturer",
        "description",
        "specs",
    ]


def test_empty_spec_value():
    product = ProductInput(
        name="Манометр",
        specs={"класс точности": "   "},
    )

    assert product.specs["класс точности"] is None
    assert "specs.класс точности" in product.missing_fields()


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_product_name(name):
    with pytest.raises(ValidationError):
        ProductInput(name=name)


def test_missing_product_name():
    with pytest.raises(ValidationError):
        ProductInput.model_validate({
            "manufacturer": "Манотомь"
        })


def test_invalid_specs_type():
    with pytest.raises(ValidationError):
        ProductInput(
            name="Манометр",
            specs=["диапазон", "точность"],
        )


def test_unknown_field():
    with pytest.raises(ValidationError):
        ProductInput.model_validate({
            "name": "Манометр",
            "unknown_field": "value",
        })


def test_invalid_json():
    with pytest.raises(ValidationError):
        ProductInput.model_validate_json(
            '{"name": "Манометр",}'
        )


def test_duplicate_spec_after_normalization():
    with pytest.raises(ValidationError):
        ProductInput(
            name="Манометр",
            specs={
                "диапазон": "0–1 МПа",
                " диапазон ": "0–2 МПа",
            },
        )
