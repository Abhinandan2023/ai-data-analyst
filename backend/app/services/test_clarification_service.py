from backend.app.services.clarification_service import ClarificationService
from backend.app.services.intent_service import IntentService
from backend.app.services.schema_inspector import get_database_schema


def test_clarification_options_for_ambiguous_customer_question():
    schema = get_database_schema()

    intent_service = IntentService()
    clarification_service = ClarificationService()

    question = "Who is the best customer?"

    analysis = intent_service.analyze(
        question=question,
        schema=str(schema),
    )

    assert analysis.ambiguous is True
    assert analysis.intent == "identify_top_customer"

    options = clarification_service.build_options(analysis)

    assert options
    assert any(
        option.value == "total_spending"
        for option in options
    )
    assert any(
        option.value == "order_count"
        for option in options
    )