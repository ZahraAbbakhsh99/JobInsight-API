from typing import Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func
from app.models.job import Job
from app.models.keyword_job import keyword_job
from scraper.JobVision import scraping_JobVision 
from scraper.Karbord import scraping_Karbord
from scraper.scrape import scrape_both_sites
from app.schemas.job import JobBase, JobCreate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import timedelta
from app.utils.link_utils import *
from app.crud.keyword_job import *
from app.crud.keyword import *

def _requirements_to_text(reqs: List[str] | None) -> str:
    if not reqs:
        return "نامشخص"
    return ",".join(reqs)

def create_jobs_bulk(db: Session, jobs_in: Iterable[JobCreate]) -> List[Job]:
    jobs_ids = []
    
    for job in jobs_in:
        success = False
        for attempt in range(2):
            try: 
                db_object = Job(
                    title=job.title,
                    salary= job.salary,
                    requirements=_requirements_to_text(job.requirements),
                    link=job.link,
                )
                db.add(db_object)
                db.flush()
                db.commit()
                jobs_ids.append(db_object.id)
                success = True
                break

            except IntegrityError:
                db.rollback()
                existing_job = db.execute(
                    select(Job).where(Job.link == job.link)
                ).scalar_one_or_none()

                if existing_job:
                    statement  = (
                        update(Job)
                        .where(Job.id == existing_job.id)
                        .values(
                            title=job.title,
                            salary=job.salary,
                            requirements=_requirements_to_text(job.requirements),
                            scraped_at=func.now()
                        )
                    )
                    db.execute(statement )
                    db.commit()
                    db.refresh(existing_job)
                    jobs_ids.append(existing_job.id)
                    success = True
                    break
            except Exception:
                db.rollback()

        if not success:
            return {"status": 0}

    return {"status": 1, "job_ids": jobs_ids}

def get_job_by_id(db: Session, job_id: int) -> Job | None:
    """
    Retrieve a Job object from the database by its ID.
    Returns None if not found.
    """
    statement = select(Job).where(Job.id == job_id)
    job = db.execute(statement).scalar_one_or_none()
    if job:
        return JobBase(
        title=job.title,
        salary=job.salary,
        requirements=job.requirements.split(",") if job.requirements else ["نامشخص"],
        link=normalize_job_link(job.link)
        )
    
    return job

def get_job_by_link(db: Session, link: str) -> Job | None:
    """
    Retrieve a Job object from the database by its link.
    Returns None if not found.
    """
    statement = select(Job).where(Job.link == link)
    job = db.execute(statement).scalar_one_or_none()
    if job:
        return JobBase(
        title=job.title,
        salary=job.salary,
        requirements=job.requirements.split(",") if job.requirements else ["نامشخص"],
        link=normalize_job_link(job.link)
        )
    
    return job

def get_jobs_by_links(db: Session, links: List[str]) -> List[JobBase]:
    """
    Retrieve multiple jobs from DB based on a list of links.
    returns List[JobBase]: Jobs found in DB, normalized and converted to JobBase
    """
    if not links:
        return []

    db_jobs = db.query(Job).filter(Job.link.in_(links)).all()

    return [
        JobBase(
            title=job.title,
            salary=job.salary,
            requirements=job.requirements.split(",") if job.requirements else ["نامشخص"],
            link=normalize_job_link(job.link)
        )
        for job in db_jobs
    ]

def delete_jobs_by_links(db: Session, links: List[str]) -> int:
    """
    Delete multiple jobs from the database based on a list of links.
    Returns Number of jobs deleted(int)
    """
    if not links:
        return 0

    try:
        stmt = delete(Job).where(Job.link.in_(links))
        result = db.execute(stmt)
        db.commit()
        return result.rowcount  # number of rows deleted
    except Exception:
        db.rollback()
        return 0

def get_jobs_by_keyword(db: Session, keyword_id: int, limit: int):
    """
    Get jobs related to a keyword with limit.
    """
    try:
        keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()
        if not keyword:
            return [], 0

        jobs_query = db.query(Job).join(Job.keywords).filter(Keyword.id == keyword_id)

        total_jobs = jobs_query.count()
        real_limit = min(limit, total_jobs)

        jobs = jobs_query.limit(real_limit).all()

        return jobs
    
    except SQLAlchemyError as e:
        # database error
        db.rollback()
        return {"status": "error", "message": str(e)}
    
    except Exception as e:
        # Error handling
         return {"status": "error", "message": f"Unexpected: {str(e)}"}
