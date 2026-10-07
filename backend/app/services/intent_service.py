from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.app.models.intent import IntentAnalysis

load_dotenv()


class IntentService:

    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        self.llm = ChatGroq(
            model=model_name,
            temperature=0,
        )

        self.structured_llm = self.llm.with_structured_output(
            IntentAnalysis
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are an Intent Analysis Engine for an AI Data Analyst.

Your job is to understand what the user wants to know from a relational
database.

Do NOT generate SQL.
Do NOT execute queries.
Do NOT invent tables, columns, metrics, or business definitions.

Analyze the user's question and determine:

1. The user's intended business operation.
2. Whether the request is ambiguous.
3. The specific missing information or ambiguity.
4. A concise clarification question when necessary.
5. Clarification options when necessary.
6. The metric explicitly specified by the user, if any.
7. Your confidence from 0.0 to 1.0.

IMPORTANT RULE:
Never guess when a business term has multiple reasonable interpretations.

For example:

"Who is the best customer?"

The word "best" is ambiguous because it could mean:

- highest total spending
- highest number of orders
- highest average order value
- highest lifetime value

Therefore, mark the request as ambiguous.

For this type of ambiguity, use these exact machine-readable identifiers:

- total_spending
- order_count
- average_order_value
- lifetime_value

Do NOT describe the ambiguity using a general natural-language phrase
such as "definition of best customer".

When the request is ambiguous:

- ambiguous must be true
- ambiguities must contain the possible interpretations
- clarification_question must contain a concise question
- clarification_options should contain appropriate choices
- metric should be null unless the user explicitly selected a metric

Each clarification option must have:

- value: machine-readable identifier
- label: human-readable description

For example:

total_spending → Highest total spending
order_count → Highest number of orders
average_order_value → Highest average order value
lifetime_value → Highest lifetime value

When the request is NOT ambiguous:

- ambiguous must be false
- ambiguities must be an empty list
- clarification_question must be null
- clarification_options must be an empty list
- metric should contain the explicitly specified metric when applicable

Examples:

"Which customer spent the most money?"

This is unambiguous.

Intent:
identify_top_customer_by_spending

Metric:
total_spending

"Who is the best customer?"

This is ambiguous.

Intent:
identify_best_customer

The system must ask the user which metric should define "best".

The intent must be a concise snake_case description of the user's
business operation.

Examples:

"Show all customers from Kolkata."
→ filter_customers_by_city

"Who spent the most money?"
→ identify_top_customer_by_spending

"How much revenue did we generate?"
→ calculate_total_revenue

"Which product sold the most?"
→ identify_top_selling_product

Use the database schema only to understand what data is available.

Do not generate SQL.

Do not assume unspecified business meanings.

When multiple reasonable interpretations exist, ask for clarification
rather than making an assumption.

A correct clarification is better than an incorrect interpretation.
""",
                ),
                (
                    "human",
                    "User question:\n{question}\n\nDatabase schema:\n{schema}",
                ),
            ]
        )

    def analyze(
        self,
        question: str,
        schema: str,
    ) -> IntentAnalysis:

        chain = self.prompt | self.structured_llm

        result = chain.invoke(
            {
                "question": question,
                "schema": schema,
            }
        )

        return result