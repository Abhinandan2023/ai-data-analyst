from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from backend.app.models.intent import (
    ResolvedIntent,
    SQLGenerationResult,
)


class SQLGenerator:

    def __init__(
        self,
        model_name: str = "openai/gpt-oss-120b",
    ):
        self.llm = ChatGroq(
            model=model_name,
            temperature=0,
        )

        self.structured_llm = self.llm.with_structured_output(
            SQLGenerationResult
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You are a PostgreSQL SQL generation engine for an AI Data Analyst.

Your job is to convert a RESOLVED business intent into a PostgreSQL
SELECT query.

The intent has already been clarified.

IMPORTANT RULES:

1. Generate ONLY a PostgreSQL SELECT query.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE,
   CREATE, GRANT, REVOKE, or any other data-modifying statement.
3. Use ONLY tables and columns present in the supplied database schema.
4. Respect the relationships defined by foreign keys.
5. Never invent tables or columns.
6. Prefer explicit column names instead of SELECT *.
7. Use correct JOIN conditions.
8. Generate a query that directly answers the resolved intent.
9. Do not execute the query.
10. Do not include markdown code fences around the SQL.
11. The SQL must be valid PostgreSQL syntax.
12. Apply relevant business rules that are explicitly provided in this prompt.

DATABASE BUSINESS RULES:

- Only orders with status = 'completed' should be included when calculating
  customer spending or revenue.
- Customer spending is calculated as:
  order_items.quantity * order_items.unit_price
- Customer spending must be aggregated across the customer's completed orders.
- When identifying the customer with the highest spending, sort the total
  spending in descending order and return the top customer.

EXAMPLE:

Resolved intent:
identify_best_customer

Metric:
total_spending

The appropriate query should:

1. Start from customers.
2. Join orders using customers.id = orders.customer_id.
3. Join order_items using orders.id = order_items.order_id.
4. Filter orders where status = 'completed'.
5. Calculate SUM(order_items.quantity * order_items.unit_price).
6. Group the result by the customer.
7. Order by total spending descending.
8. Return the highest-spending customer.

Do not assume additional business rules that are not provided.

Return a brief explanation of what the query calculates.
""",
                ),
                (
                    "human",
                    """
Resolved intent:
{intent}

Metric:
{metric}

Filters:
{filters}

Database schema:
{schema}
""",
                ),
            ]
        )

    def generate(
        self,
        resolved_intent: ResolvedIntent,
        schema: str,
    ) -> SQLGenerationResult:

        chain = self.prompt | self.structured_llm

        result = chain.invoke(
            {
                "intent": resolved_intent.intent,
                "metric": resolved_intent.metric,
                "filters": resolved_intent.filters,
                "schema": schema,
            }
        )

        return result