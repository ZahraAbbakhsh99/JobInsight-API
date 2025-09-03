from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import *
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.schemas.auth import AuthRequest, AuthResponse, VerifyOtpRequest
from app.models.users import User
from app.models.otps import Otp
from app.models.tokens import Token
from database.session import get_db
from datetime import timedelta
from app.utils.auth_utils import *

router = APIRouter(tags=["Authentication"])

@router.post("/auth/send-otp")
async def authenticate_user(request: AuthRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email (part1).
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(email=request.email)
        db.add(user)
        db.commit()
        db.refresh(user)

    code = generate_otp()
    expires_at = db.query(func.now()).scalar() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    otp = Otp(user_id=user.id, code=code, expires_at=expires_at)
    db.add(otp)
    db.commit()

    return {"message": f"OTP = {code}"}


@router.post("/auth/verify-otp", response_model=AuthResponse)
async def verify_otp(request: VerifyOtpRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with email (part2).
    """
     
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    otp = db.query(Otp).filter(
        Otp.user_id == user.id,
        Otp.code == request.code,
        Otp.is_used == False,
        Otp.expires_at > func.now()
    ).first()

    if not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP")

    otp.is_used = True
    db.commit()

    token_str, expires_at = create_jwt(user.id, db)
    token = Token(user_id=user.id, token=token_str, expires_at=expires_at)
    db.add(token)
    db.commit()

    return {"access_token": token_str}
