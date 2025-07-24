from typing import Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.job import Job
from app.schemas.job import JobCreate

def _requirements_to_text(reqs: List[str] | None) -> str:
    if not reqs:
        return "نامشخص"
    return "-".join(reqs)

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
    for job_in in jobs_in:
        existing = get_by_link(db, job_in.link)
        if existing:
            saved.append(existing)
            continue
        db_obj = Job(
            title=job_in.title,
            salary=int(job_in.salary) if isinstance(job_in.salary, str) and job_in.salary.isdigit() else None,
            requirements=_requirements_to_text(job_in.requirements),
            link=job_in.link,
            posted_at=None,
        )
        db.add(db_obj)
        saved.append(db_obj)
    db.commit()

    for obj in saved:
        try:
            db.refresh(obj)
        except:
            pass
    return saved
