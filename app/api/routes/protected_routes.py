from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.csv import *
from app.schemas.job import *
from sqlalchemy.orm import Session
from app.services.auth import get_current_user
from database.session import get_db
from app.crud.keyword import *
from app.crud.queue import *
from app.crud.job import get_jobs_by_keyword
from app.services.csv import *
import uuid

router = APIRouter(tags=["Jobs"])

@router.post("/jobs/download", response_model=CSVResponse)
async def download_jobs_csv(request: CSVRequest,
                            db: Session = Depends(get_db), 
                            current_user = Depends(get_current_user)):
    """
    Generate a CSV file with job postings and 
    return a link to download the file.
    If keyword is not yet processed, 
    queue it and notify the user by email when ready.
    """

    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    keyword_result = get_keyword(db , request.keyword)
    if keyword_result["status"]:
        keyword_id = keyword_result["id"]
    elif keyword_result["status"] == 0:
        add_keyword_to_queue(db, request.keyword, user_id=current_user.id)
        
        return DetailResponse(
            detail=f"Your request will be queued and you will be notified by email {current_user.email} once it has been processed."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword '{request.keyword}' not found"
        )

    if request.limit == 0:
       return {"jobs": [], "keyword_id": request.keyword}
    
    jobs = get_jobs_by_keyword(db, keyword_id, request.limit)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for this keyword")
    
    filename = f"jobs_{request.keyword}_{uuid.uuid4().hex}.csv"
    filepath = save_jobs_to_csv(jobs, filename)

    download_link = f"/files/{filename}"

    return CSVResponse(download_link=download_link)