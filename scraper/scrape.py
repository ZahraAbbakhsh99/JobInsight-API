from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord
from typing import List
from app.schemas.job import JobBase

def scrape_jobs(keyword: str) -> List[JobBase]:
    """
    Scrape jobs from both JobVision and Karbord without a limit.
    Combines results from both sites into a single list.
    """
    jobs_jobvision = scraping_JobVision(keyword)
    jobs_karbord = scraping_Karbord(keyword)

    Scraped_job: List[JobBase] = jobs_jobvision + jobs_karbord

    return Scraped_job