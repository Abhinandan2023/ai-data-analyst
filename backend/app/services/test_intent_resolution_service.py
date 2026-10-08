import pytest

from backend.app.models.intent import (
    IntentAnalysis,
    ClarificationOption,
)
from backend.app.services.intent_resolution_service import (
    IntentResolutionService,
)


def create_ambiguous_analysis():
    return IntentAnalysis(
        intent="identify_top_customer",
        ambiguous=True,
        ambiguities=[
            "total_spending",
            "order_count",
            "average_order_value",
            "lifetime_value",
        ],
        clarification_question="Which metric should define the best customer?",
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
        confidence=0.9,
        metric=None,
        filters={},
    )


def test_resolve_valid_clarification_option():
    service = IntentResolutionService()

    analysis = create_ambiguous_analysis()

    resolved = service.resolve(
        analysis=analysis,
        selected_option="total_spending",
    )

    assert resolved.intent == "identify_top_customer"
    assert resolved.metric == "total_spending"
    assert resolved.filters == {}


def test_resolve_invalid_clarification_option():
    service = IntentResolutionService()

    analysis = create_ambiguous_analysis()

    with pytest.raises(
        ValueError,
        match="Invalid clarification option: invalid_metric",
    ):
        service.resolve(
            analysis=analysis,
            selected_option="invalid_metric",
        )