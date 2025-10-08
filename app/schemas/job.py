from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List

class JobBase(BaseModel):
    title: str
    salary: Optional[str] = None
    link: str
    skills: List[str]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("skills", mode="before")
    def parse_skills(cls, v):
        if not v:
            return []
        if isinstance(v, str):
            v = v.replace("،", ",")
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [str(s).strip() for s in v if str(s).strip()]
        return []
    
class JobCreate(JobBase):
    pass

class JobOut(JobBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class JobRequest(BaseModel):
    keyword: str
    limit: Optional[int] = 10

    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    jobs: List[JobBase]

    model_config = ConfigDict(from_attributes=True)

class DetailResponse(BaseModel):
    detail: str

    model_config = ConfigDict(from_attributes=True)