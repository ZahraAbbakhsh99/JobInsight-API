from fastapi import APIRouter, Header, HTTPException
from app.schemas.csv import *
from app.utils.token_utils import *

router = APIRouter(tags=["Jobs"])

@router.post("/jobs/download", response_model=CSVResponse)
async def download_jobs_csv(request: CSVRequest, 
                            authorization: str = Header(..., description="Bearer token for authentication")):
    """
    Generate a CSV file with job postings and 
    return a link to download the file.
    """
    # the CSV should be created and saved on the server.
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"download_link": "https://api.example.com/files/mock123.csv"}