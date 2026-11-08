from types import SimpleNamespace

import pytest

from product_cards.generator import generate_card
from product_cards.models import GeneratedText, ProductInput


class FakeResponses:
    def __init__(self, parsed):
        self.parsed = parsed
        self.called_with = None

    def parse(self, **kwargs):
        self.called_with = kwargs
        return SimpleNamespace(output_parsed=self.parsed)


class FakeClient:
    def __init__(self, parsed):
        self.responses = FakeResponses(parsed)


def make_generated_text():
    return GeneratedText(
        seo_title="Манометр DM 02",
        seo_description="Описание манометра",
        search_queries=[
            "манометр DM 02",
            "манометр купить",
            "манометр Манотомь",
        ],
        commercial_text="Прибор для измерения давления",
    )


def test_generate_card_preserves_specs():
    client = FakeClient(make_generated_text())

    product = ProductInput(
        name="Манометр DM 02",
        specs={"класс точности": "1,5"},
    )

    card = generate_card(
        product=product,
        client=client,
        model="test-model",
    )

    assert card.characteristics == {
        "класс точности": "1,5"
    }

    assert card.seo_title == "Манометр DM 02"
    assert client.responses.called_with["model"] == "test-model"


def test_missing_characteristic():
    client = FakeClient(make_generated_text())

    product = ProductInput(
        name="Манометр",
        specs={"класс точности": None},
    )

    card = generate_card(
        product=product,
        client=client,
        model="test-model",
    )

    assert card.characteristics["класс точности"] == "данных нет"
    assert "specs.класс точности" in card.missing_fields


def test_empty_llm_result():
    client = FakeClient(None)

    product = ProductInput(name="Манометр")

    with pytest.raises(RuntimeError):
        generate_card(
            product=product,
            client=client,
            model="test-model",
        )
