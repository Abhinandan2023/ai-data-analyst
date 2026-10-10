from unittest.mock import MagicMock, patch

from backend.app.models.intent import (
    ResolvedIntent,
    SQLGenerationResult,
)
from backend.app.services.sql_pipeline import SQLPipeline


def test_sql_pipeline_generates_and_validates_query():
    resolved_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

    generated_result = SQLGenerationResult(
        sql="""
            SELECT
                c.id,
                c.name,
                SUM(oi.quantity * oi.unit_price) AS total_spending
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name
            ORDER BY total_spending DESC
            LIMIT 1
        """,
        explanation="Finds the highest-spending customer.",
    )

    with patch(
        "backend.app.services.sql_pipeline.SQLGenerator"
    ) as mock_generator_class:
        mock_generator = MagicMock()
        mock_generator.generate.return_value = generated_result
        mock_generator_class.return_value = mock_generator

        pipeline = SQLPipeline()

        sql = pipeline.generate_and_validate(
            resolved_intent=resolved_intent,
        )

    assert sql
    assert sql.upper().startswith("SELECT")
    assert "customers" in sql.lower()
    assert "orders" in sql.lower()
    assert "order_items" in sql.lower()
    assert "total_spending" in sql.lower()

    mock_generator.generate.assert_called_once()