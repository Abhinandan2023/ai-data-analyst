from pprint import pprint
from backend.app.models.intent_types import IntentType
from backend.app.models.intent import (
    ClarificationOption,
    IntentAnalysis,
)
from backend.app.services.intent_resolution_service import (
    IntentResolutionService,
)


analysis = IntentAnalysis(
    intent=IntentType.IDENTIFY_TOP_CUSTOMER,
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
    confidence=0.99,
    metric=None,
)

service = IntentResolutionService()

resolved = service.resolve(
    analysis=analysis,
    selected_option="total_spending",
)

pprint(resolved.model_dump())

try:
    service.resolve(
        analysis=analysis,
        selected_option="invalid_metric",
    )
except ValueError as e:
    print("\nInvalid option test:")
    print(e)