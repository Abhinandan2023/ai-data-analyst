from backend.app.models.intent import ResolvedIntent
from backend.app.services.schema_inspector import get_database_schema
from backend.app.services.sql_generator import SQLGenerator
from backend.app.services.sql_validator import SQLValidator


class SQLPipeline:

    def __init__(self):
        self.generator = SQLGenerator()
        self.validator = SQLValidator()

    def generate_and_validate(
        self,
        resolved_intent: ResolvedIntent,
    ) -> str:

        schema = get_database_schema()

        generated = self.generator.generate(
            resolved_intent=resolved_intent,
            schema=str(schema),
        )

        validated_sql = self.validator.validate(
            generated.sql
        )

        return validated_sql