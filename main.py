from database.base import Base
from database.session import engine
from fastapi import FastAPI
from app.api.routes import auth, jobs, protected_routes
from app.models.users import User
from app.models.tokens import Token
from app.models.otps import Otp
from app.models.job import Job
from app.models.keyword import Keyword
from app.models.keyword_job import keyword_job
from app.models.keyword_queue import KeywordQueue
from fastapi.staticfiles import StaticFiles
from app.worker.scheduler import *

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    start_scheduler()

    # test
    add_on_demand_job("python")

# Auth
app.include_router(auth.router ,prefix="")

# Jobs
app.include_router(jobs.router, prefix="")

# export
app.include_router(protected_routes.router, prefix="")

# serve static files
app.mount("/files", StaticFiles(directory="files"), name="files")

@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()