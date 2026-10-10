from sqlalchemy.orm import Session

from backend.app.models.intent import ResolvedIntent
from backend.app.services.answer_formatter import AnswerFormatter
from backend.app.services.sql_executor import SQLExecutor
from backend.app.services.sql_pipeline import SQLPipeline


class AnalysisService:

    def __init__(self):
        self.sql_pipeline = SQLPipeline()
        self.sql_executor = SQLExecutor()
        self.answer_formatter = AnswerFormatter()

    def analyze(
        self,
        db: Session,
        resolved_intent: ResolvedIntent,
    ) -> dict:


        sql = self.sql_pipeline.generate_and_validate(
            resolved_intent
        )

        rows = self.sql_executor.execute(
            db=db,
            sql=sql,
        )
        answer = self.answer_formatter.format(
            resolved_intent=resolved_intent,
            rows=rows,
        )

        return {
            "sql": sql,
            "rows": rows,
            "answer": answer,
        }