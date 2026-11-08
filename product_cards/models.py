from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    manufacturer: str | None = None
    specs: dict[str, str | None] = Field(default_factory=dict)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название товара не может быть пустым")

        return value

    @field_validator("manufacturer", "description")
    @classmethod
    def normalize_optional_text(
        cls, value: str | None
    ) -> str | None:
        if value is None:
            return None

        return value.strip() or None

    @field_validator("specs")
    @classmethod
    def normalize_specs(
        cls, specs: dict[str, str | None]
    ) -> dict[str, str | None]:
        result = {}

        for key, value in specs.items():
            cleaned_key = key.strip()

            if not cleaned_key:
                raise ValueError(
                    "Название характеристики не может быть пустым"
                )

            if cleaned_key in result:
                raise ValueError(
                    f"Повторяющаяся характеристика: {cleaned_key}"
                )

            result[cleaned_key] = (
                value.strip() or None
                if value is not None
                else None
            )

        return result

    def missing_fields(self) -> list[str]:
        missing = []

        if self.manufacturer is None:
            missing.append("manufacturer")

        if self.description is None:
            missing.append("description")

        if not self.specs:
            missing.append("specs")

        for key, value in self.specs.items():
            if value is None:
                missing.append(f"specs.{key}")

        return missing
