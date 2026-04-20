from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get(
    "/summary",
    response_model=schemas.AnalyticsSummary,
    responses={400: {"model": schemas.ErrorResponse}, 500: {"model": schemas.ErrorResponse}},
)
def get_summary(db: Session = Depends(get_db)):
    return crud.get_analytics_summary(db=db)
