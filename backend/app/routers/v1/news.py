from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.news import NewsFlash
from app.schemas.v1_schemas import NewsResponse

router = APIRouter(prefix="/news", tags=["News Flash Bulletins"])

@router.get("", response_model=List[NewsResponse])
def get_news_flash(db: Session = Depends(get_db)):
    """Returns incident reports and disaster bulletins from other regions."""
    return db.query(NewsFlash).order_by(desc(NewsFlash.published_at)).limit(20).all()
