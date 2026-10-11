
from decimal import Decimal
from typing import Any

from backend.app.models.intent import ResolvedIntent


class AnswerFormatter:
    """Convert SQL query results into readable business answers."""

    @staticmethod
    def _get_value(
        row: dict[str, Any],
        *keys: str,
        default: Any = None,
    ) -> Any:
        """Return the first available, non-None value."""
        for key in keys:
            value = row.get(key)
            if value is not None:
                return value

        return default

    @staticmethod
    def _format_number(value: Any) -> str:
        """Format numeric values with thousands separators and 2 decimals."""
        if value is None:
            return "N/A"

        if isinstance(value, (int, float, Decimal)):
            return f"{value:,.2f}"

        return str(value)

    @staticmethod
    def _format_currency(value: Any) -> str:
        """Format monetary values in Indian rupees."""
        return f"₹{AnswerFormatter._format_number(value)}"

    @staticmethod
    def _format_name(row: dict[str, Any]) -> str:
        """Get a readable customer or product name."""
        return str(
            AnswerFormatter._get_value(
                row,
                "name",
                "customer_name",
                "product_name",
                "full_name",
                default="The record",
            )
        )

    @staticmethod
    def _format_cell(value: Any) -> str:
        """Format an individual value for readable text output."""
        if value is None:
            return "N/A"

        if isinstance(value, (Decimal, float)):
            return f"{value:,.2f}"

        return str(value)

    def _format_rows(self, rows: list[dict[str, Any]]) -> str:
        """Format multiple SQL rows as a readable numbered list."""
        formatted_rows = []

        for index, result_row in enumerate(rows, start=1):
            values = ", ".join(
                f"{key.replace('_', ' ')}: {self._format_cell(value)}"
                for key, value in result_row.items()
            )
            formatted_rows.append(f"{index}. {values}")

        return "\n".join(formatted_rows)

    def format(
        self,
        resolved_intent: ResolvedIntent,
        rows: list[dict[str, Any]],
    ) -> str:
        """Format SQL results according to the resolved intent and metric."""
        if not rows:
            return "No matching records were found."

        intent = resolved_intent.intent
        metric = resolved_intent.metric

        # Normalize metric aliases.
        metric_aliases = {
            "total_quantity": "quantity_sold",
            "total_quantity_sold": "quantity_sold",
            "units_sold": "quantity_sold",
            "revenue": "total_revenue",
            "total_spend": "total_spending",
            "avg_order_value": "average_order_value",
            "orders_count": "order_count",
            "total_orders": "order_count",
            "customer_lifetime_value": "lifetime_value",
        }

        metric = metric_aliases.get(metric, metric)
        row = rows[0]

        # 1. Highest-spending customer.
        if (
            intent == "identify_top_customer"
            and metric == "total_spending"
        ):
            name = self._format_name(row)
            amount = self._get_value(
                row,
                "total_spending",
                "total_revenue",
                "total_amount",
            )

            if amount is not None:
                return (
                    f"{name} is the highest-spending customer, "
                    f"with total spending of "
                    f"{self._format_currency(amount)}."
                )

        # 2. Customer with the most completed orders.
        if (
            intent == "identify_top_customer"
            and metric == "order_count"
        ):
            name = self._format_name(row)
            count = self._get_value(
                row,
                "order_count",
                "orders_count",
                "total_orders",
            )

            if count is not None:
                return (
                    f"{name} has the highest number of completed orders, "
                    f"with {count} orders."
                )

        # 3. Customer with the highest average order value.
        if (
            intent == "identify_top_customer"
            and metric == "average_order_value"
        ):
            name = self._format_name(row)
            average = self._get_value(
                row,
                "average_order_value",
                "avg_order_value",
            )

            if average is not None:
                return (
                    f"{name} has the highest average order value, "
                    f"at {self._format_currency(average)}."
                )

        # 4. Customer with the highest lifetime value.
        if (
            intent == "identify_top_customer"
            and metric == "lifetime_value"
        ):
            name = self._format_name(row)
            lifetime_value = self._get_value(
                row,
                "lifetime_value",
                "customer_lifetime_value",
            )

            if lifetime_value is not None:
                return (
                    f"{name} has the highest customer lifetime value, "
                    f"at {self._format_currency(lifetime_value)}."
                )

        # 5. Product generating the highest revenue.
        if (
            intent == "identify_top_product"
            and metric == "total_revenue"
        ):
            name = self._format_name(row)
            revenue = self._get_value(
                row,
                "total_revenue",
                "revenue",
                "total_sales",
            )

            if revenue is not None:
                return (
                    f"{name} generates the highest revenue, "
                    f"with total sales of "
                    f"{self._format_currency(revenue)}."
                )

        # 6. Product with the highest quantity sold.
        if (
            intent == "identify_top_product"
            and metric == "quantity_sold"
        ):
            products = []

            for product in rows:
                name = self._get_value(
                    product,
                    "product_name",
                    "name",
                    default="The product",
                )
                quantity = self._get_value(
                    product,
                    "total_quantity_sold",
                    "total_quantity",
                    "quantity_sold",
                    "units_sold",
                )

                if quantity is not None:
                    products.append((str(name), quantity))

            if products:
                highest_quantity = max(
                    quantity for _, quantity in products
                )

                top_products = [
                    name
                    for name, quantity in products
                    if quantity == highest_quantity
                ]

                if len(top_products) == 1:
                    return (
                        f"{top_products[0]} has the highest number "
                        f"of units sold, with {highest_quantity} units."
                    )

                names = (
                    ", ".join(top_products[:-1])
                    + f" and {top_products[-1]}"
                )

                return (
                    f"{names} are tied for the highest number "
                    f"of units sold, with {highest_quantity} units each."
                )

        # 7. Average order value across orders.
        if (
            intent == "calculate_average_order_value"
            and metric == "average_order_value"
        ):
            average = self._get_value(
                row,
                "average_order_value",
                "avg_order_value",
            )

            if average is not None:
                return (
                    f"The average order value is "
                    f"{self._format_currency(average)}."
                )

        # 8. Total revenue.
        if (
            intent == "calculate_total_revenue"
            and metric == "total_revenue"
        ):
            revenue = self._get_value(
                row,
                "total_revenue",
                "revenue",
                "total_sales",
            )

            if revenue is not None:
                return (
                    f"The total revenue is "
                    f"{self._format_currency(revenue)}."
                )

        # 9. Generic fallback: show actual SQL results.
        if len(rows) == 1:
            values = [
                f"{key.replace('_', ' ')}: {self._format_cell(value)}"
                for key, value in row.items()
            ]

            return "The query result is: " + "; ".join(values) + "."

        return (
            f"The query returned {len(rows)} matching records:\n"
            + self._format_rows(rows)
        )
