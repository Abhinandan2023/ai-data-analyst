from backend.app.db.connection import SessionLocal
from backend.app.models.intent import ResolvedIntent
from backend.app.services.analysis_service import AnalysisService
from backend.app.models.intent_types import IntentType


def test_analysis_service():

    service = AnalysisService()

    resolved_intent = ResolvedIntent(
        intent=IntentType.IDENTIFY_TOP_CUSTOMER,
        metric="total_spending",
    )

    db = SessionLocal()

    try:
        result = service.analyze(
            db=db,
            resolved_intent=resolved_intent,
        )

        print("\nGenerated SQL:")
        print(result["sql"])

        print("\nRows:")
        print(result["rows"])

        print("\nFinal Answer:")
        print(result["answer"])

        assert result["rows"]
        assert "Rahul Sharma" in result["answer"]
        assert "219,000.00" in result["answer"]

        print("\nAnalysis service test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    test_analysis_service()