from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func
from database.base import Base

class KeywordQueue(Base):
    __tablename__ = "keyword_queue"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False)
    user_id = Column(Integer, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, done
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
