from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.models.intent import (
    ClarificationOption,
    IntentAnalysis,
    SQLGenerationResult,
)

client = TestClient(app)


def test_analyze_requires_clarification_for_ambiguous_question():
    expected_analysis = IntentAnalysis(
        intent="identify_top_customer",
        ambiguous=True,
        ambiguities=["The meaning of 'best customer' is unclear."],
        clarification_question="How should the best customer be determined?",
        clarification_options=[
            ClarificationOption(
                value="total_spending",
                label="Highest total spending",
            ),
            ClarificationOption(
                value="order_count",
                label="Highest number of orders",
            ),
        ],
        confidence=0.95,
        metric=None,
        filters={},
    )

    with patch(
        "backend.app.services.analysis_orchestrator.IntentService.analyze",
        return_value=expected_analysis,
    ):
        response = client.post(
            "/analyze",
            json={"question": "Who is the best customer?"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "clarification_required"
    assert data["answer"] is None
    assert data["clarification_question"] is not None
    assert len(data["clarification_options"]) > 0
    assert data["sql"] is None


def test_analyze_resolves_order_count_and_returns_answer():
    expected_analysis = IntentAnalysis(
        intent="identify_top_customer",
        ambiguous=True,
        ambiguities=["The meaning of 'best customer' is unclear."],
        clarification_question="How should the best customer be determined?",
        clarification_options=[
            ClarificationOption(
                value="total_spending",
                label="Highest total spending",
            ),
            ClarificationOption(
                value="order_count",
                label="Highest number of orders",
            ),
        ],
        confidence=0.95,
        metric=None,
        filters={},
    )

    generated_result = SQLGenerationResult(
        sql="""
            SELECT
                c.id,
                c.name,
                COUNT(DISTINCT o.id) AS order_count
            FROM customers c
            JOIN orders o ON c.id = o.customer_id
            WHERE o.status = 'completed'
            GROUP BY c.id, c.name
            ORDER BY order_count DESC
            LIMIT 1
        """,
        explanation="Finds the customer with the most completed orders.",
    )

    with (
        patch(
            "backend.app.services.analysis_orchestrator.IntentService.analyze",
            return_value=expected_analysis,
        ),
        patch(
            "backend.app.services.sql_generator.SQLGenerator.generate",
            return_value=generated_result,
        ),
    ):
        response = client.post(
            "/analyze",
            json={
                "question": "Who is the best customer?",
                "selected_option": "order_count",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "completed"
    assert data["answer"] is not None
    assert "highest number of completed orders" in data["answer"]
    assert "order_count" in data["sql"].lower()
    assert "count" in data["sql"].lower()