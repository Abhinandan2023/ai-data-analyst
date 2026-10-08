from backend.app.services.intent_service import IntentService
from backend.app.services.schema_inspector import get_database_schema


def test_analyze_ambiguous_customer_question():
    schema = get_database_schema()

    service = IntentService()

    result = service.analyze(
        question="Who is the best customer?",
        schema=str(schema),
    )

    assert result.intent == "identify_top_customer"
    assert result.ambiguous is True
    assert result.metric is None

    assert result.clarification_options

    option_values = {
        option.value
        for option in result.clarification_options
    }

    assert "total_spending" in option_values
    assert "order_count" in option_values


def test_analyze_total_revenue():
    schema = get_database_schema()

    service = IntentService()

    result = service.analyze(
        question="What is our total revenue?",
        schema=str(schema),
    )

    assert result.intent == "calculate_total_revenue"
    assert result.ambiguous is False
    assert result.metric == "total_revenue"
    assert result.clarification_options == []