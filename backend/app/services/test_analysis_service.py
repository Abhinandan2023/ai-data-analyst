from backend.app.db.connection import SessionLocal
from backend.app.models.intent import ResolvedIntent
from backend.app.services.analysis_service import AnalysisService


def test_analysis_service():

    service = AnalysisService()

    db = SessionLocal()

    try:
        # Test 1: Top customer
        customer_intent = ResolvedIntent(
            intent="identify_top_customer",
            metric="total_spending",
            filters={},
        )

        customer_result = service.analyze(
            db=db,
            resolved_intent=customer_intent,
        )

        print("\n--- Customer Analysis ---")

        print("\nGenerated SQL:")
        print(customer_result["sql"])

        print("\nRows:")
        print(customer_result["rows"])

        print("\nFinal Answer:")
        print(customer_result["answer"])

        assert customer_result["rows"]
        assert "Rahul Sharma" in customer_result["answer"]
        assert "219,000.00" in customer_result["answer"]

        # Test 2: Total revenue
        revenue_intent = ResolvedIntent(
            intent="calculate_total_revenue",
            metric="total_revenue",
            filters={},
        )

        revenue_result = service.analyze(
            db=db,
            resolved_intent=revenue_intent,
        )

        print("\n--- Revenue Analysis ---")

        print("\nGenerated SQL:")
        print(revenue_result["sql"])

        print("\nRows:")
        print(revenue_result["rows"])

        print("\nFinal Answer:")
        print(revenue_result["answer"])

        assert revenue_result["rows"]
        assert "440,500.00" in revenue_result["answer"]

        print("\nAnalysis service tests passed.")

    finally:
        db.close()


if __name__ == "__main__":
    test_analysis_service()