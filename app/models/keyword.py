from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from .base import Base

class Keyword(Base):
    __tablename__ = "keyword"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Text, nullable=False, unique=True)

    jobs = relationship("Job", secondary="keyword_job", back_populates="keywords")
