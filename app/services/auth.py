
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from database.session import get_db
from app.models.tokens import Token
from sqlalchemy import func
from typing import Optional

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
):
    if not api_key:
        return None

    if api_key.lower().startswith("bearer "):
        token_str = api_key.split(" ", 1)[1]
    else:
        raise HTTPException(status_code=401, detail="Invalid token format")

    db_token = db.query(Token).filter(Token.token == token_str).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_time = db.query(func.now()).scalar()
    if db_token.expires_at < current_time:
        raise HTTPException(status_code=401, detail="Token expired")

    return db_token.user
