import tempfile
import os
from app.schemas.job import *
from openpyxl import Workbook
from fastapi.responses import FileResponse

def save_jobs_to_csv(jobs: list[JobBase], filename) -> str:
    """
    Save jobs to an Excel (.xlsx) file and return the file path.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "JobInsight"

    filepath = filename

    tmp_dir = tempfile.mkdtemp()
    filepath = os.path.join(tmp_dir, filepath)

    # header
    headers = ["title", "salary", "link", "skills"]
    ws.append(headers)

    # rows
    for job in jobs:
        ws.append([
            job.title,
            job.salary or "",
            job.link,
            job.skills
        ])

    wb.save(filepath)
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
        background=lambda: os.remove(filepath)
    )
    # return filepath