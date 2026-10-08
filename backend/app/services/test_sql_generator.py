from pprint import pprint

from backend.app.models.intent import ResolvedIntent
from backend.app.models.intent_types import IntentType
from backend.app.services.schema_inspector import get_database_schema
from backend.app.services.sql_generator import SQLGenerator


schema = get_database_schema()

resolved_intent = ResolvedIntent(
    intent=IntentType.IDENTIFY_TOP_CUSTOMER,
    metric="total_spending",
)

generator = SQLGenerator()

result = generator.generate(
    resolved_intent=resolved_intent,
    schema=str(schema),
)

pprint(result.model_dump())