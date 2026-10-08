from sqlalchemy.orm import Session
from backend.app.services.schema_inspector import get_database_schema
from backend.app.models.intent import ResolvedIntent
from backend.app.services.analysis_service import AnalysisService
from backend.app.services.clarification_service import ClarificationService
from backend.app.services.intent_resolution_service import IntentResolutionService
from backend.app.services.intent_service import IntentService


class AnalysisOrchestrator:

    def __init__(self):
        self.intent_service = IntentService()
        self.clarification_service = ClarificationService()
        self.intent_resolution_service = IntentResolutionService()
        self.analysis_service = AnalysisService()

    def analyze(
        self,
        db: Session,
        question: str,
        selected_option: str | None = None,
    ) -> dict:

        schema = get_database_schema()

        intent_analysis = self.intent_service.analyze(
        question=question,
        schema=schema,
        )

        print("\n--- Intent Analysis ---")
        print(intent_analysis.model_dump())
 
        if intent_analysis.ambiguous and selected_option is None:

            options = self.clarification_service.build_options(
                intent_analysis
            )

            return {
                "status": "clarification_required",
                "answer": None,
                "clarification_question": (
                    intent_analysis.clarification_question
                ),
                "clarification_options": options,
                "sql": None,
            }


        if intent_analysis.ambiguous:
            resolved_intent = self.intent_resolution_service.resolve(
                analysis=intent_analysis,
                selected_option=selected_option,
            )
        else:
            resolved_intent = self.intent_resolution_service.resolve(
                analysis=intent_analysis,
                selected_option="",
            )

        print("\n--- Resolved Intent ---")
        print(resolved_intent.model_dump())

  
        result = self.analysis_service.analyze(
            db=db,
            resolved_intent=resolved_intent,
        )

      
        return {
            "status": "completed",
            "answer": result["answer"],
            "clarification_question": None,
            "clarification_options": [],
            "sql": result["sql"],
        }
    