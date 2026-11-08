import json
import sys

import httpx
import pytest
from openai import RateLimitError

import main


@pytest.fixture
def product_file(tmp_path):
    path = tmp_path / "product.json"

    path.write_text(
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

    return path


@pytest.fixture
def run_cli(monkeypatch, capsys):
    def _run(*args):
        monkeypatch.setattr(
            sys,
            "argv",
            ["main.py", *map(str, args)],
        )

        exit_code = main.main()
        captured = capsys.readouterr()

        return exit_code, captured

    return _run


def test_file_not_found(run_cli, tmp_path):
    missing_file = tmp_path / "not_found.json"

    exit_code, output = run_cli(
        missing_file,
        "--validate-only",
    )

    assert exit_code == 1
    assert "Ошибка" in output.err


def test_malformed_json(run_cli, tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text(
        '{"name":',
        encoding="utf-8",
    )

    exit_code, output = run_cli(
        path,
        "--validate-only",
    )

    assert exit_code == 1
    assert "Ошибка" in output.err


def test_empty_product_name(run_cli, tmp_path):
    path = tmp_path / "empty_name.json"

    path.write_text(
        '{"name": "   "}',
        encoding="utf-8",
    )

    exit_code, output = run_cli(
        path,
        "--validate-only",
    )

    assert exit_code == 1
    assert "Ошибка" in output.err


def test_missing_api_key(
    run_cli,
    product_file,
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "load_dotenv",
        lambda: None,
    )
    monkeypatch.setenv("OPENAI_API_KEY", "")

    exit_code, output = run_cli(product_file)

    assert exit_code == 1
    assert "OPENAI_API_KEY" in output.err


def test_invalid_output_extension(
    run_cli,
    product_file,
    tmp_path,
):
    output_path = tmp_path / "card.txt"

    exit_code, output = run_cli(
        product_file,
        "--output",
        output_path,
    )

    assert exit_code == 1
    assert ".json" in output.err
    assert ".md" in output.err
    assert not output_path.exists()


def test_api_quota_error(
    run_cli,
    product_file,
    monkeypatch,
):
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses",
    )

    response = httpx.Response(
        status_code=429,
        request=request,
        json={
            "error": {
                "code": "credit_balance_exhausted",
                "type": "insufficient_quota",
                "message": "No credits remaining",
            }
        },
    )

    class FakeResponses:
        def parse(self, **kwargs):
            raise RateLimitError(
                "No credits remaining",
                response=response,
                body=response.json(),
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.responses = FakeResponses()

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "fake-test-key",
    )

    monkeypatch.setattr(
        main,
        "OpenAI",
        FakeOpenAI,
    )

    exit_code, output = run_cli(product_file)

    assert exit_code == 1
    assert "429" in output.err
