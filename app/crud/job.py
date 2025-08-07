from typing import Iterable, List
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from app.models.job import Job
from app.schemas.job import JobCreate
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from datetime import datetime

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