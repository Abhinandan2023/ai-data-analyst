from backend.app.models.intent import ResolvedIntent
from backend.app.services.answer_formatter import AnswerFormatter


formatter = AnswerFormatter()


def test_format_top_customer():
    customer_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

    customer_rows = [
        {
            "id": 1,
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "total_spending": 219000.00,
        }
    ]

    answer = formatter.format(
        resolved_intent=customer_intent,
        rows=customer_rows,
    )

    assert answer == (
        "Rahul Sharma is the highest-spending customer, "
        "with total spending of ₹219,000.00."
    )


def test_format_total_revenue():
    revenue_intent = ResolvedIntent(
        intent="calculate_total_revenue",
        metric="total_revenue",
        filters={},
    )

    revenue_rows = [
        {
            "total_revenue": 440500.00,
        }
    ]

    answer = formatter.format(
        resolved_intent=revenue_intent,
        rows=revenue_rows,
    )

    assert answer == "The total revenue is ₹440,500.00."


def test_format_empty_result():
    customer_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

    answer = formatter.format(
        resolved_intent=customer_intent,
        rows=[],
    )

    assert answer == "No matching records were found."


def test_format_top_customer_by_order_count():
    formatter = AnswerFormatter()

    resolved_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="order_count",
        filters={},
    )

    rows = [
        {
            "name": "Rahul Sharma",
            "order_count": 5,
        }
    ]

    result = formatter.format(
        resolved_intent=resolved_intent,
        rows=rows,
    )

    assert result == (
        "Rahul Sharma has the highest number of completed orders, "
        "with 5 orders."
    )