from unittest.mock import MagicMock, patch

from backend.app.db.connection import SessionLocal
from backend.app.models.intent import ResolvedIntent
from backend.app.services.analysis_service import AnalysisService


def test_analysis_service():
    service = AnalysisService()
    db = SessionLocal()

    try:
        customer_intent = ResolvedIntent(
            intent="identify_top_customer",
            metric="total_spending",
            filters={},
        )

        customer_sql = """
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
        """

        revenue_intent = ResolvedIntent(
            intent="calculate_total_revenue",
            metric="total_revenue",
            filters={},
        )

        revenue_sql = """
            SELECT SUM(oi.quantity * oi.unit_price) AS total_revenue
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status = 'completed'
        """

        with patch.object(
            service.sql_pipeline,
            "generate_and_validate",
            side_effect=[customer_sql, revenue_sql],
        ):
            customer_result = service.analyze(
                db=db,
                resolved_intent=customer_intent,
            )

            assert customer_result["rows"]
            assert "Rahul Sharma" in customer_result["answer"]
            assert "219,000.00" in customer_result["answer"]

            revenue_result = service.analyze(
                db=db,
                resolved_intent=revenue_intent,
            )

            assert revenue_result["rows"]
            assert "440,500.00" in revenue_result["answer"]

    finally:
        db.close()