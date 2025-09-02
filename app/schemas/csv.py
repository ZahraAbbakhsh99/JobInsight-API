from pydantic import BaseModel
from typing import Optional

class CSVRequest(BaseModel):
    keyword: str
    limit: Optional[int] = 50

class CSVResponse(BaseModel):
    download_link: str