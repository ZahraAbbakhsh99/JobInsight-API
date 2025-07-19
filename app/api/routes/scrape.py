from fastapi import APIRouter
from schemas.scrape import ScrapeRequest, ScrapedJob
from typing import List

router = APIRouter()

@router.post("/scrape/", response_model=List[ScrapedJob])
def scrape_jobs(request: ScrapeRequest):

    pass

    return [
        ScrapedJob(
            title=f"{request.keyword} Developer",
            salary="Negotiable",
            link="http://example.com/job/1",
            requirements=["Python", "FastAPI", "SQL"]
        ),
        ScrapedJob(
            title=f"{request.keyword} ",
            salary="Negotiable",
            link="http://example.com/job/2",
            requirements=["Python"]
        )
    ]
