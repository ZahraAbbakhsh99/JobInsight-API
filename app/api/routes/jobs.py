from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.job import *
from sqlalchemy.orm import Session
from database.session import get_db
from app.crud.keyword import get_keyword
from app.crud.job import get_jobs_by_keyword
from app.models.users import User
from app.services.auth import get_current_user
from typing import Union

router = APIRouter(tags=["Jobs"])

@router.post("/jobs", response_model=Union[JobResponse, DetailResponse])
async def get_jobs(request: JobRequest, 
                   db: Session = Depends(get_db),
                   current_user: Optional[User] = Depends(get_current_user)):
    """
    Return a list of job postings based on a keyword and limit.
    """
    #  we should call the scraping service here.
    
    keyword_result = get_keyword(db , request.keyword)
    if keyword_result["status"]:
        keyword_id = keyword_result["id"]
    elif keyword_result["status"] == 0:
       # It must be queued for processing...
        if current_user:
            return DetailResponse(
                detail=f"Your request will be queued and you will be notified by email {current_user.email} once it has been processed."
            )
        else:
            return DetailResponse(
                detail="Your request cannot be processed at this time and has been placed in a queue."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword '{request.keyword}' not found"
        )

    if request.limit == 0:
       return {"jobs": [], "keyword_id": request.keyword}
    
    jobs = get_jobs_by_keyword(db, keyword_id, request.limit)

    return JobResponse(
        jobs=[JobBase.from_orm(job) for job in jobs]
    )

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