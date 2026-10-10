
from backend.app.models.intent import ResolvedIntent


class AnswerFormatter:
    def format(
        self,
        resolved_intent: ResolvedIntent,
        rows: list[dict],
    ) -> str:
        if not rows:
            return "No matching records were found."

        row = rows[0]

        if (
            resolved_intent.intent == "identify_top_customer"
            and resolved_intent.metric == "total_spending"
        ):
            name = row.get("name") or row.get("customer_name")
            total_spending = row["total_spending"]

            return (
                f"{name} is the highest-spending customer, "
                f"with total spending of ₹{total_spending:,.2f}."
            )

        if (
            resolved_intent.intent == "identify_top_customer"
            and resolved_intent.metric == "order_count"
        ):
            name = row.get("name") or row.get("customer_name")
            order_count = row["order_count"]

            return (
                f"{name} has the highest number of completed orders, "
                f"with {order_count} orders."
            )

        if (
            resolved_intent.intent == "identify_top_customer"
            and resolved_intent.metric == "average_order_value"
        ):
            name = row.get("name") or row.get("customer_name")
            average = row.get(
                "average_order_value",
                row.get("avg_order_value"),
            )

            return (
                f"{name} has the highest average order value, "
                f"at ₹{average:,.2f}."
            )

        if (
            resolved_intent.intent == "identify_top_customer"
            and resolved_intent.metric == "lifetime_value"
        ):
            name = row.get("name") or row.get("customer_name")
            lifetime_value = row["lifetime_value"]

            return (
                f"{name} has the highest customer lifetime value, "
                f"at ₹{lifetime_value:,.2f}."
            )

        if (
            resolved_intent.intent == "calculate_total_revenue"
            and resolved_intent.metric == "total_revenue"
        ):
            total_revenue = row["total_revenue"]
            return f"The total revenue is ₹{total_revenue:,.2f}."

        return f"Query returned {len(rows)} result(s)."
