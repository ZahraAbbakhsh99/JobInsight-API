from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord

def scrape_both_sites(keyword: str, limit : int):

    jobvision_count = int(limit * 0.6)
    karbord_count = limit - jobvision_count

    jobs_jobvision = scraping_JobVision(keyword, jobvision_count)
    jobs_karbord = scraping_Karbord(keyword, karbord_count)

    Scraped_job = jobs_jobvision + jobs_karbord

    return Scraped_job