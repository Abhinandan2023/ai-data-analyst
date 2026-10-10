from unittest.mock import MagicMock, patch

from backend.app.models.intent import (
    ResolvedIntent,
    SQLGenerationResult,
)
from backend.app.services.sql_generator import SQLGenerator


def test_sql_generator_generates_top_customer_query():
    expected_result = SQLGenerationResult(
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
        explanation=(
            "Finds the customer with the highest spending "
            "across completed orders."
        ),
    )

    resolved_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

    with patch(
        "backend.app.services.sql_generator.ChatGroq"
    ) as mock_chat_groq:
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_prompt = MagicMock()
        mock_chain = MagicMock()

        mock_chat_groq.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_prompt.__or__.return_value = mock_chain

        with patch(
            "backend.app.services.sql_generator.ChatPromptTemplate.from_messages",
            return_value=mock_prompt,
        ):
            generator = SQLGenerator()

        mock_chain.invoke.return_value = expected_result

        result = generator.generate(
            resolved_intent=resolved_intent,
            schema="Test database schema",
        )

    assert result.sql
    assert result.explanation

    sql = result.sql.upper()

    assert "SELECT" in sql
    assert "CUSTOMERS" in sql
    assert "ORDERS" in sql
    assert "ORDER_ITEMS" in sql
    assert "SUM" in sql
    assert "TOTAL_SPENDING" in sql
    assert "LIMIT 1" in sql

    mock_chain.invoke.assert_called_once_with(
        {
            "intent": "identify_top_customer",
            "metric": "total_spending",
            "filters": {},
            "schema": "Test database schema",
        }
    )