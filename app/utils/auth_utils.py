import random
import string
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.session import get_db
from fastapi import Depends
from datetime import datetime, timedelta

JWT_SECRET = "YOUR_SECRET_KEY"
JWT_ALGORITHM = "HS256"
OTP_EXPIRE_MINUTES = 10
TOKEN_EXPIRE_HOURS = 24

def generate_otp(length: int = 6):
    return ''.join(random.choices(string.digits, k=length))

def create_jwt(user_id: int, db: Session = Depends(get_db)):

    current_time = db.query(func.now()).scalar()
    expire_time = current_time + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "exp": expire_time}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, expire_time
