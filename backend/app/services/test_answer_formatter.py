from backend.app.models.intent import ResolvedIntent
from backend.app.models.intent_types import IntentType
from backend.app.services.answer_formatter import AnswerFormatter


formatter = AnswerFormatter()


# Test 1: Top customer
customer_intent = ResolvedIntent(
    intent=IntentType.IDENTIFY_TOP_CUSTOMER,
    metric="total_spending",
)

customer_rows = [
    {
        "id": 1,
        "name": "Rahul Sharma",
        "email": "rahul@example.com",
        "total_spending": 219000.00,
    }
]

customer_answer = formatter.format(
    resolved_intent=customer_intent,
    rows=customer_rows,
)

print(customer_answer)


# Test 2: Total revenue
revenue_intent = ResolvedIntent(
    intent=IntentType.CALCULATE_TOTAL_REVENUE,
    metric="total_revenue",
)

revenue_rows = [
    {
        "total_revenue": 440500.00,
    }
]

revenue_answer = formatter.format(
    resolved_intent=revenue_intent,
    rows=revenue_rows,
)

print(revenue_answer)


# Test 3: Empty result
empty_answer = formatter.format(
    resolved_intent=customer_intent,
    rows=[],
)

print(empty_answer)

print("All answer formatter tests passed.")