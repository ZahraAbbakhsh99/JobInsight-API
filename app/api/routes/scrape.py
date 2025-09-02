from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.scrape import ScrapeRequest, ScrapedJob
from typing import List
from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord
from scraper.scrape import scrape_both_sites
from app.schemas.job import JobCreate, JobOut
from app.crud.job import create_jobs_bulk, get_jobs_for_keyword
from app.crud.keyword import get_keyword, create_keyword
from app.crud.keyword_job import create_keyword_job_relations
from database.session import get_db

router = APIRouter()

@router.post("/scrape/", response_model=List[ScrapedJob])
def scrape_jobs(request: ScrapeRequest, db: Session = Depends(get_db)):

    """
    Scrape job listings from JobVision and Karbord based on the keyword and limit provided.

    The function splits the total job count as:
    - 60% from JobVision
    - 40% from Karbord

    Args:
        request (ScrapeRequest): Contains the search keyword and max number of jobs(limit).

    Returns:
        List[ScrapedJob]: A unified list of structured job postings.
    """

    keyword_result = get_keyword(db , request.keyword)
    keyword_id = keyword_result["id"]
    
    if request.limit == 0:
       return {"jobs": [], "keyword_id": None}
    
    elif request.limit == 1 :
        if not keyword_id: 
            keyword_id = create_keyword(db, request.keyword)["id"]

            jobs = scraping_JobVision(request.keyword, request.limit)

        elif keyword_id:
            pass
            result = get_jobs_for_keyword(db,keyword_id, request.limit)
            if "jobs" not in result:
                raise HTTPException(status_code=500, detail=f"Jobs key missing. Result: {result}")
            jobs = result["jobs"]
        else: 
            raise HTTPException(status_code=400, detail="Invalid keyword.")

    else: 
        if not keyword_id :

            jobs = scrape_both_sites(request.keyword, request.limit)

        elif keyword_id:
            pass
            result = get_jobs_for_keyword(db,keyword_id, request.limit)
            if "jobs" not in result:
                raise HTTPException(status_code=500, detail=f"Jobs key missing. Result: {result}")
            jobs = result["jobs"]
        else: 
            raise HTTPException(status_code=400, detail="Invalid keyword status.")

    jobs_result = create_jobs_bulk(db, jobs)
    if jobs_result["status"]:
        if create_keyword_job_relations(db, keyword_id, jobs_result["job_ids"]):
            return jobs
    
    # _____ return result without storage 
    # all_jobs = jobs_jobvision + jobs_karbord
    # return all_jobs

    # _____ mock result
    # return [
    #     ScrapedJob(
    #         title=f"{request.keyword} Developer",
    #         salary="Negotiable",
    #         link="http://example.com/job/1",
    #         requirements=["Python", "FastAPI", "SQL"]
    #     ),
    #     ScrapedJob(
    #         title=f"{request.keyword} ",
    #         salary="Negotiable",
    #         link="http://example.com/job/2",
    #         requirements=["Python"]
    #     )
    # ]