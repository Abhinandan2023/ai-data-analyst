from backend.app.models.intent import ResolvedIntent
from backend.app.services.schema_inspector import get_database_schema
from backend.app.services.sql_generator import SQLGenerator


def test_sql_generator_generates_top_customer_query():
    schema = get_database_schema()

    generator = SQLGenerator()

    resolved_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

    result = generator.generate(
        resolved_intent=resolved_intent,
        schema=str(schema),
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