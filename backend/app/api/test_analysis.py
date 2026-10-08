from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_analyze_requires_clarification_for_ambiguous_question():
    response = client.post(
        "/analyze",
        json={
            "question": "Who is the best customer?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "clarification_required"
    assert data["answer"] is None
    assert data["clarification_question"] is not None
    assert len(data["clarification_options"]) > 0
    assert data["sql"] is None


def test_analyze_resolves_order_count_and_returns_answer():
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