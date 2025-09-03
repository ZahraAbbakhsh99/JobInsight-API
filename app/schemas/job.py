from pydantic import BaseModel
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    salary: Optional[str] = None
    link: str
    skills: List[str]

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: int

    class Config:
        from_attributes = True

class JobRequest(BaseModel):
    keyword: str
    limit: Optional[int] = 10

class JobResponse(BaseModel):
    jobs: List[JobBase]
