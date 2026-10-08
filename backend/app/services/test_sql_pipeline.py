from backend.app.models.intent import ResolvedIntent
from backend.app.services.sql_pipeline import SQLPipeline


def test_sql_pipeline_generates_and_validates_query():
    resolved_intent = ResolvedIntent(
        intent="identify_top_customer",
        metric="total_spending",
        filters={},
    )

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