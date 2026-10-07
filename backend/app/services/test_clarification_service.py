from pprint import pprint

from backend.app.services.clarification_service import ClarificationService
from backend.app.services.intent_service import IntentService
from backend.app.services.schema_inspector import get_database_schema


schema = get_database_schema()

intent_service = IntentService()
clarification_service = ClarificationService()

question = "Who is the best customer?"

analysis = intent_service.analyze(
    question=question,
    schema=str(schema),
)

options = clarification_service.build_options(analysis)

print("\n--- Intent Analysis ---")
pprint(analysis.model_dump())

print("\n--- Clarification Options ---")
pprint([option.model_dump() for option in options])