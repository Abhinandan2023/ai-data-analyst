from backend.app.models.intent import ResolvedIntent


class AnswerFormatter:

    def format(
        self,
        resolved_intent: ResolvedIntent,
        rows: list[dict],
    ) -> str:

        if not rows:
            return "No matching records were found."

        if (
            resolved_intent.intent == "identify_top_customer"
            and resolved_intent.metric == "total_spending"
        ):
            row = rows[0]

            name = row["name"]
            total_spending = row["total_spending"]

            return (
                f"{name} is the highest-spending customer, "
                f"with total spending of ₹{total_spending:,.2f}."
            )

        if (
            resolved_intent.intent == "calculate_total_revenue"
            and resolved_intent.metric == "total_revenue"
        ):
            total_revenue = rows[0]["total_revenue"]

            return f"The total revenue is ₹{total_revenue:,.2f}."

        return f"Query returned {len(rows)} result(s)."