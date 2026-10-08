from backend.app.models.intent import ResolvedIntent
from backend.app.models.intent_types import IntentType


class AnswerFormatter:

    def format(
        self,
        resolved_intent: ResolvedIntent,
        rows: list[dict],
    ) -> str:

        if not rows:
            return "No matching records were found."

        if (
            resolved_intent.intent == IntentType.IDENTIFY_TOP_CUSTOMER
            and resolved_intent.metric == "total_spending"
        ):
            row = rows[0]

            name = row["name"]
            total_spending = row["total_spending"]

            return (
                f"{name} is the highest-spending customer, "
                f"with total spending of ₹{total_spending:,.2f}."
            )

        return f"Query returned {len(rows)} result(s)."