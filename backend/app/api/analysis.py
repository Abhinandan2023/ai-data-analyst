from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.connection import get_db
from backend.app.models.analysis import AnalysisRequest, AnalysisResponse
from backend.app.services.analysis_orchestrator import AnalysisOrchestrator


router = APIRouter()

orchestrator = AnalysisOrchestrator()


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):
    return orchestrator.analyze(
        db=db,
        question=request.question,
        selected_option=request.selected_option,
    )