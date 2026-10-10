from backend.app.models.intent import (
    ClarificationOption,
    IntentAnalysis,
)
from backend.app.services.clarification_service import ClarificationService


def test_clarification_options_for_ambiguous_customer_question():
    analysis = IntentAnalysis(
        intent="identify_top_customer",
        ambiguous=True,
        ambiguities=["The meaning of 'best customer' is unclear."],
        clarification_question="How should the best customer be determined?",
        clarification_options=[
            ClarificationOption(
                value="total_spending",
                label="Highest total spending",
            ),
            ClarificationOption(
                value="order_count",
                label="Highest number of orders",
            ),
            ClarificationOption(
                value="average_order_value",
                label="Highest average order value",
            ),
            ClarificationOption(
                value="lifetime_value",
                label="Highest lifetime value",
            ),
        ],
        confidence=0.95,
        metric=None,
        filters={},
    )

    clarification_service = ClarificationService()

    options = clarification_service.build_options(analysis)

    assert len(options) == 4
    assert any(
        option.value == "total_spending"
        for option in options
    )
    assert any(
        option.value == "order_count"
        for option in options
    )


def test_clarification_options_are_empty_for_unambiguous_question():
    analysis = IntentAnalysis(
        intent="calculate_total_revenue",
        ambiguous=False,
        ambiguities=[],
        clarification_question=None,
        clarification_options=[],
        confidence=0.98,
        metric="total_revenue",
        filters={},
    )

    clarification_service = ClarificationService()

    options = clarification_service.build_options(analysis)

    assert options == []