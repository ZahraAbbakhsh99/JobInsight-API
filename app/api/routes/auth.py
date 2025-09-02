from fastapi import APIRouter
from app.schemas.auth import *


router = APIRouter(tags=["Authentication"])

@router.post("/auth", response_model=AuthResponse)
async def authenticate_user(request: AuthRequest):
    """
    Authenticate user with email.
    """

    # we should send verify email, then generate and return a JWT token.

    return {"access_token": "fake-token-for-demo"}