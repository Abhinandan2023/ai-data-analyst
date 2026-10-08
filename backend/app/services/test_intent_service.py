from pprint import pprint

from backend.app.services.intent_service import IntentService
from backend.app.services.schema_inspector import get_database_schema


schema = get_database_schema()

service = IntentService()

question = "Who is the best customer?"

result = service.analyze(
    question=question,
    schema=str(schema),
)

pprint(result.model_dump())

revenue_result = service.analyze(
    question="What is our total revenue?",
    schema=schema,
)

print("\nRevenue Intent Test:")
pprint(revenue_result.model_dump())