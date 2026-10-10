from unittest.mock import patch
from groq import APIError
from sqlalchemy.exc import SQLAlchemyError

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

def test_analyze_rejects_invalid_clarification_option():
    with patch(
        "backend.app.api.analysis.orchestrator.analyze",
        side_effect=ValueError(
            "Invalid clarification option: invalid_metric"
        ),
    ):
        response = client.post(
            "/analyze",
            json={
                "question": "Who is the best customer?",
                "selected_option": "invalid_metric",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid clarification option: invalid_metric"
    )

def test_analyze_returns_503_when_groq_fails():
    with patch(
        "backend.app.api.analysis.orchestrator.analyze",
        side_effect=APIError(
            "Groq service unavailable",
            request=None,
            body=None,
        ),
    ):
        response = client.post(
            "/analyze",
            json={"question": "What is our total revenue?"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The AI service is temporarily unavailable. Please try again later."
    )

def test_analyze_returns_503_when_database_fails():
    with patch(
        "backend.app.api.analysis.orchestrator.analyze",
        side_effect=SQLAlchemyError("Database connection failed"),
    ):
        response = client.post(
            "/analyze",
            json={"question": "What is our total revenue?"},
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The database service is temporarily unavailable. Please try again later."
    )
