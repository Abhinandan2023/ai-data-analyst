from unittest.mock import MagicMock, patch

from backend.app.models.intent import (
    ClarificationOption,
    IntentAnalysis,
)
from backend.app.services.intent_service import IntentService


def run_intent_service_test(question, expected_result):
    with patch(
        "backend.app.services.intent_service.ChatGroq"
    ) as mock_chat_groq:
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_prompt = MagicMock()
        mock_chain = MagicMock()

        mock_chat_groq.return_value = mock_llm
        mock_llm.with_structured_output.return_value = mock_structured_llm

        # Mock: prompt | structured_llm
        mock_prompt.__or__.return_value = mock_chain

        with patch(
            "backend.app.services.intent_service.ChatPromptTemplate.from_messages",
            return_value=mock_prompt,
        ):
            service = IntentService()

        mock_chain.invoke.return_value = expected_result

        result = service.analyze(
            question=question,
            schema="Test database schema",
        )

        mock_chain.invoke.assert_called_once_with(
            {
                "question": question,
                "schema": "Test database schema",
            }
        )

        return result


def test_analyze_ambiguous_customer_question():
    expected_result = IntentAnalysis(
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

    result = run_intent_service_test(
        question="Who is the best customer?",
        expected_result=expected_result,
    )

    assert result.intent == "identify_top_customer"
    assert result.ambiguous is True
    assert result.metric is None

    option_values = {
        option.value
        for option in result.clarification_options
    }

    assert "total_spending" in option_values
    assert "order_count" in option_values


def test_analyze_total_revenue():
    expected_result = IntentAnalysis(
        intent="calculate_total_revenue",
        ambiguous=False,
        ambiguities=[],
        clarification_question=None,
        clarification_options=[],
        confidence=0.98,
        metric="total_revenue",
        filters={},
    )

    result = run_intent_service_test(
        question="What is our total revenue?",
        expected_result=expected_result,
    )

    assert result.intent == "calculate_total_revenue"
    assert result.ambiguous is False
    assert result.metric == "total_revenue"
    assert result.clarification_options == []