from decimal import Decimal

from backend.app.models.intent import ResolvedIntent
from backend.app.services.answer_formatter import AnswerFormatter


formatter = AnswerFormatter()


def test_format_best_customer():

    resolved_intent = ResolvedIntent(
        intent="identify_best_customer",
        metric="total_spending",
    )

    rows = [
        {
            "id": 1,
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "total_spending": Decimal("219000.00"),
        }
    ]

    answer = formatter.format(
        resolved_intent=resolved_intent,
        rows=rows,
    )

    print(answer)

    assert answer == (
        "Rahul Sharma is the highest-spending customer, "
        "with total spending of ₹219,000.00."
    )


def test_format_no_results():

    resolved_intent = ResolvedIntent(
        intent="identify_best_customer",
        metric="total_spending",
    )

    answer = formatter.format(
        resolved_intent=resolved_intent,
        rows=[],
    )

    print(answer)

    assert answer == "No matching records were found."


if __name__ == "__main__":
    test_format_best_customer()
    test_format_no_results()

    print("All answer formatter tests passed.")