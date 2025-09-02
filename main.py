from database.base import Base
from database.session import engine
from fastapi import FastAPI
from app.api.routes import auth, jobs, protected_routes

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# Auth
app.include_router(auth.router ,prefix="")

# Jobs
app.include_router(jobs.router, prefix="")

# export
app.include_router(protected_routes.router, prefix="")

