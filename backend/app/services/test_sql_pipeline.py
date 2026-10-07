from backend.app.models.intent import ResolvedIntent
from backend.app.services.sql_pipeline import SQLPipeline


resolved_intent = ResolvedIntent(
    intent="identify_best_customer",
    metric="total_spending",
)

pipeline = SQLPipeline()

sql = pipeline.generate_and_validate(
    resolved_intent=resolved_intent,
)

print("\n--- Validated SQL ---")
print(sql)