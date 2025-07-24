from pydantic import BaseModel
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    salary: Optional[str] = None
    requirements: List[str]
    link: str

class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: int

    class Config:
        orm_mode = True
