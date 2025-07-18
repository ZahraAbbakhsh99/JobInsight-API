from database.base import Base
from database.session import engine
from fastapi import FastAPI
from app.models.job import Job
from app.models.keyword import Keyword
from app.models.keyword_job import keyword_job

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
