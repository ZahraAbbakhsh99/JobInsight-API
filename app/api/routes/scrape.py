from fastapi import APIRouter
from app.schemas.scrape import ScrapeRequest, ScrapedJob
from typing import List
from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord

router = APIRouter()

@router.post("/scrape/", response_model=List[ScrapedJob])
def scrape_jobs(request: ScrapeRequest):

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
    
    jobvision_count = int(request.limit * 0.6)
    karbord_count = request.limit - jobvision_count

    jobs_jobvision = scraping_JobVision(request.keyword, jobvision_count)
    jobs_karbord = scraping_Karbord(request.keyword, karbord_count)

    all_jobs = jobs_jobvision + jobs_karbord
    return all_jobs

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
