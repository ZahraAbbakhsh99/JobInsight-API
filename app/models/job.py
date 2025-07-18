from sqlalchemy import Column, Integer, String, Text, BigInteger, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    salary = Column(BigInteger, nullable=True)
    requirements = Column(Text, nullable=False)
    link = Column(Text, nullable=False, unique=True)
    posted_at = Column(TIMESTAMP, nullable=True)
    scraped_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    keywords = relationship("Keyword", secondary="keyword_job", back_populates="jobs")
