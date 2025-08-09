from sqlalchemy import select, update, func
from sqlalchemy.orm import Session
from app.models.keyword_job import keyword_job

def create_keyword_job_relations(db: Session, keyword_id: int, job_ids: list[int]) -> dict:
    """
    Create relations between a keyword and multiple jobs in the keyword_job table.

    Args:
        db (Session): SQLAlchemy database session.
        keyword_id (int): The ID of the keyword.
        job_ids (list[int]): A list of job IDs to link to the keyword.

    Returns:
        dict: {
            "status": 1   -> all relations successfully created,
            "status": 0   -> no relation created,
            "status": -1  -> partial success,
        }
    """
    all_success = True
    any_success = False

    for job_id in job_ids:
        # Check if the relation already exists
        exists = db.execute(
            select(keyword_job.c.keyword_id).where(
                keyword_job.c.keyword_id == keyword_id,
                keyword_job.c.job_id == job_id
            )
        ).scalar_one_or_none()

        if exists:
            # Update last_update for existing relation
            db.execute(
                update(keyword_job)
                .where(
                    keyword_job.c.keyword_id == keyword_id,
                    keyword_job.c.job_id == job_id
                )
                .values(last_update=func.now())
            )
            db.commit()
            any_success = True
            continue  # Skip existing relations

        success = False
        for attempt in range(2):  # Retry logic
            try:
                db.execute(
                    keyword_job.insert().values(
                        keyword_id=keyword_id,
                        job_id=job_id
                    )
                )
                db.commit()
                success = True
                break
            except Exception:
                db.rollback()

        if success:
            any_success = True
        else:
            all_success = False

    if not any_success:
        status = 0
    elif all_success:
        status = 1
    else:
        status = -1

    return {
        "status": status,
    }
