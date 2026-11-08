from product_cards.models import GeneratedText


class CardQualityError(RuntimeError):
    """Ошибка качества сгенерированной карточки."""


def validate_generated_text(
    generated: GeneratedText,
) -> list[str]:
    errors = []
    warnings = []

    # 1. Проверяем SEO-заголовок
    title = generated.seo_title

    if not title.strip():
        errors.append("SEO-заголовок пустой")
    elif len(title) > 70:
        errors.append(
            f"SEO-заголовок: {len(title)} символов, "
            "максимум 70"
        )

    # 2. Проверяем SEO-описание
    description = generated.seo_description

    if not description.strip():
        errors.append("SEO-описание пустое")
    elif len(description) > 1200:
        errors.append(
            f"SEO-описание: {len(description)} символов, "
            "максимум 1200"
        )
    elif len(description) < 800:
        warnings.append(
            f"SEO-описание содержит {len(description)} "
            "символов вместо рекомендуемых 800–1200. "
            "Требуется доработка."
        )

    # 3. Проверяем количество поисковых запросов
    queries = generated.search_queries

    if not 3 <= len(queries) <= 5:
        errors.append(
            f"Поисковых запросов: {len(queries)}, "
            "допустимо от 3 до 5"
        )

    # 4. Проверяем пустые запросы и дубликаты
    normalized_queries = [
        query.strip().casefold()
        for query in queries
    ]

    if any(not query for query in normalized_queries):
        errors.append("Обнаружен пустой поисковый запрос")

    if len(normalized_queries) != len(set(normalized_queries)):
        errors.append("Обнаружены повторяющиеся запросы")

    # 5. Проверяем коммерческий блок
    if not generated.commercial_text.strip():
        errors.append("Коммерческий блок пустой")

    if errors:
        raise CardQualityError(
            "Карточка не прошла проверку:\n- "
            + "\n- ".join(errors)
        )

    return warnings
