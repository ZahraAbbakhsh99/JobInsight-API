from sqlalchemy import Column, Integer, ForeignKey, Table, TIMESTAMP
from sqlalchemy.sql import func
from database.base import Base

keyword_job = Table(
    "keyword_job",
    Base.metadata,
    Column("keyword_id", Integer, ForeignKey("keyword.id", ondelete="CASCADE"), primary_key=True),
    Column("job_id", Integer, ForeignKey("job.id", ondelete="CASCADE"), primary_key=True),
    Column("last_update", TIMESTAMP, nullable=False, server_default=func.now())
)
