from pydantic import BaseModel
from typing import List

class ScrapeRequest(BaseModel):
    keyword: str
    limit: int

class ScrapedJob(BaseModel):
    title: str
    salary: str | None = None
    link: str
    requirements: List[str]
