from fastapi import Depends, Header, HTTPException
from app.models.tokens import Token
from app.models.users import User
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database.session import get_db


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)) -> User:
    """
    Returns the User associated with a valid token.
    Raises HTTPException 401 if token is missing, invalid, or expired.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if authorization.lower().startswith("bearer "):
        token_str = authorization.split(" ", 1)[1]
    else:
        raise HTTPException(status_code=401, detail="Invalid token format")

    db_token = db.query(Token).filter(Token.token == token_str).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_time = db.query(func.now()).scalar()
    if db_token.expires_at < current_time:
        raise HTTPException(status_code=401, detail="Token expired")

    return db_token.user

def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> Optional[User]:
    """
    Returns the User associated with a valid token.
    If no token is provided, returns None.
    Raises HTTPException 401 only if a token is provided but invalid/expired.
    """
    if not authorization:
        return None  # no token provided

    if authorization.lower().startswith("bearer "):
        token_str = authorization.split(" ", 1)[1]
    else:
        raise HTTPException(status_code=401, detail="Invalid token format")

    db_token = db.query(Token).filter(Token.token == token_str).first()
    if not db_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_time = db.query(func.now()).scalar()
    if db_token.expires_at < current_time:
        raise HTTPException(status_code=401, detail="Token expired")

    return db_token.user
