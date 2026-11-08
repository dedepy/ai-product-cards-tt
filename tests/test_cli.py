import json
import sys
from types import SimpleNamespace

import main
from product_cards.models import GeneratedText


class FakeResponses:
    def parse(self, **kwargs):
        assert kwargs["text_format"] is GeneratedText

        return SimpleNamespace(
            output_parsed=GeneratedText(
                seo_title="Манометр DM 02",
                seo_description=(
                    "Тестовое описание манометра DM 02."
                ),
                search_queries=[
                    "манометр DM 02",
                    "манометр показывающий",
                    "манометр Манотомь",
                ],
                commercial_text=(
                    "Прибор для измерения давления."
                ),
            )
        )


class FakeOpenAI:
    def __init__(self, **kwargs):
        self.responses = FakeResponses()


def test_cli_generation_without_real_api(
    monkeypatch,
    tmp_path,
    capsys,
):
    product_file = tmp_path / "product.json"

    product_file.write_text(
        json.dumps(
            {
                "name": "Манометр DM 02",
                "manufacturer": "Манотомь",
                "specs": {
                    "класс точности": "1,5"
                },
                "description": "Прибор для измерения давления",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key-not-real",
    )

    monkeypatch.setenv(
        "OPENAI_MODEL",
        "gpt-5-mini",
    )

    monkeypatch.setattr(
        main,
        "OpenAI",
        FakeOpenAI,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", str(product_file)],
    )

    exit_code = main.main()

    captured = capsys.readouterr()

    assert exit_code == 0

    result = json.loads(captured.out)

    assert result["seo_title"] == "Манометр DM 02"

    assert result["characteristics"] == {
        "класс точности": "1,5"
    }

    assert result["missing_fields"] == []
