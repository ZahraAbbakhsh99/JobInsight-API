from typing import Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.job import Job
from app.schemas.job import JobCreate
from app.schemas.scrape import ScrapedJob

def _requirements_to_text(reqs: List[str] | None) -> str:
    if not reqs:
        return "نامشخص"
    return ",".join(reqs)

def _requirements_to_list(reqs: str | None) -> List[str]:
    if not reqs:
        return ["نامشخص"]
    return [r.strip() for r in reqs.split("-")]


def get_by_link(db: Session, link: str) -> Job | None:
    return db.execute(select(Job).where(Job.link == link)).scalar_one_or_none()

def create_job(db: Session, job_in: JobCreate) -> Job:
    
    if get_by_link(db, job_in.link):
        return get_by_link(db, job_in.link)

    db_object = Job(
        title=job_in.title,
        salary = job_in.salary,
        requirements=_requirements_to_text(job_in.requirements),
        link=job_in.link
    )
    db.add(db_object)
    db.commit()
    db.refresh(db_object)
    return db_object

def create_jobs_bulk(db: Session, jobs_in: Iterable[JobCreate]) -> List[Job]:
    saved: List[Job] = []
    seen_links = set()
    
    for job_in in jobs_in:
        existing =job_in.link in seen_links or get_by_link(db, job_in.link)
        if existing:
            saved.append(existing)
            continue
        db_object = Job(
            title=job_in.title,
            salary= job_in.salary,
            requirements=_requirements_to_text(job_in.requirements),
            link=job_in.link,
        )
        db.add(db_object)
        saved.append(db_object)
        seen_links.add(job_in.link)
    db.commit()

    for object in saved:
        try:
            db.refresh(object)
        except:
            pass
    return [
        ScrapedJob(
            title=object.title,
            salary=object.salary,
            link=object.link,
            requirements=_requirements_to_list(object.requirements)
        )
    ]