from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.scrape import ScrapeRequest, ScrapedJob
from typing import List
from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord
from app.schemas.job import JobCreate, JobOut
from app.crud.job import create_jobs_bulk
from database.session import get_db
import re

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
    if request.limit == 0:
        return []
    elif request.limit == 1 :
        jobs_jobvision = scraping_JobVision(request.keyword, request.limit)
        jobs_karbord =[]
    else: 
        jobvision_count = int(request.limit * 0.6)
        karbord_count = request.limit - jobvision_count

        jobs_jobvision = scraping_JobVision(request.keyword, jobvision_count)
        jobs_karbord = scraping_Karbord(request.keyword, karbord_count)

    # map scraped dicts -> JobCreate
    to_create: List[JobCreate] = [
        JobCreate(
            title=job["title"],
            salary=job.get("salary"),
            requirements=job.get("requirements", ["نامشخص"]),
            link=normalize_job_link(job["link"])
        )
        for job in (jobs_jobvision + jobs_karbord)
    ]
    jobs_result = create_jobs_bulk(db, to_create)
    if jobs_result["status"]:
        return to_create
    
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



def normalize_job_link(link: str) -> str:
    """
    Normalize job links from known sources like JobVision or Karbord.
    Returns a cleaned link containing only the base + unique ID.
    """
    if "jobvision.ir" in link:
        match = re.search(r'/jobs/(\d+)', link)
        if match:
            job_id = match.group(1)
            return f"https://jobvision.ir/jobs/{job_id}"
        
    elif "karbord.io" in link:
        match = re.search(r'/jobs/detail/(\d+)', link)
        if match:
            job_id = match.group(1)
            return f"https://karbord.io/jobs/detail/{job_id}"

    # fallback: return original if not matched
    return link