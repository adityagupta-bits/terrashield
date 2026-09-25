from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db.session import Base

class NewsFlash(Base):
    __tablename__ = "news_flash"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    region = Column(String(100), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String(100), default="National Disaster Management Authority (NDMA)")
    published_at = Column(DateTime, default=datetime.utcnow, index=True)
