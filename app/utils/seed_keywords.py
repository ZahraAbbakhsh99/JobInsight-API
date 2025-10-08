from sqlalchemy.orm import Session
from app.worker.scraper.scrape import scrape_jobs
from app.crud.job import create_jobs_with_keyword
from app.crud.keyword import *

def seed_initial_keywords(db: Session, keywords: list[str]):
    """
    Seed initial keywords into the database and scrape their jobs.
    
    Args:
        db (Session): SQLAlchemy DB session
        keywords (list[str]): List of keywords to scrape
    """
    for keyword_text in keywords:
        result = get_keyword(db, keyword_text)
        if result.get("status") == 1:
            print(f"Keyword '{keyword_text}' already exists or error occurred")
            continue
        
        # log scraping start
        print(f"Scraping jobs for keyword: {keyword_text}")
        # run scraper for this keyword
        jobs = scrape_jobs(keyword_text)
        # save scraped jobs to database and link them to keyword
        create_jobs_with_keyword(db, keyword_text, jobs)
        # log completion
        print(f"Keyword '{keyword_text}' processed and jobs saved to DB")
