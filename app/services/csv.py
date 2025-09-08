import csv
from pathlib import Path
from fastapi import HTTPException
from app.schemas.job import *

FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

def save_jobs_to_csv(jobs: list[JobBase], filename: str) -> str:
    """
    Save jobs to a CSV file and return the path
    """
    filepath = FILES_DIR / filename
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # header
        writer.writerow(["title", "salary", "link", "skills"])
        # rows
        for job in jobs:
            writer.writerow([job.title, job.salary or "", job.link, ",".join(job.skills)])
    return str(filepath)
