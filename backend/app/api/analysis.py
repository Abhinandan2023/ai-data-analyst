from fastapi import APIRouter, Depends, HTTPException
from groq import APIError
from sqlalchemy.exc import SQLAlchemyError
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
    try:
        return orchestrator.analyze(
            db=db,
            question=request.question,
            selected_option=request.selected_option,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except APIError as exc:
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable. Please try again later.",
        ) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="The database service is temporarily unavailable. Please try again later.",
        ) from exc