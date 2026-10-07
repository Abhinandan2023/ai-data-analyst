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