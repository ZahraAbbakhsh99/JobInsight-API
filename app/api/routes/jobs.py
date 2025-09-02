from fastapi import APIRouter
from app.schemas.job import *

router = APIRouter(tags=["Jobs"])

@router.post("/jobs", response_model=JobResponse)
async def get_jobs(request: JobRequest):
    """
    Return a list of job postings based on a keyword and limit.
    """
    #  we should call the scraping service here.
    
    mock_jobs_data = [
    {
        "title": "Python Developer",
        "salary": "Negotiable",
        "link": "https://jobvision.ir/job/123",
        "skills": ["Django", "FastAPI", "SQL"]
    },
    {
        "title": "Frontend Developer",
        "salary": "7000-9000",
        "link": "https://jobvision.ir/job/124",
        "skills": ["React", "TypeScript", "CSS"]
    }
    ]
    jobs_list = [JobBase(**job) for job in mock_jobs_data]
    return JobResponse(jobs=jobs_list)