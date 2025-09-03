from pydantic import BaseModel, EmailStr

class AuthRequest(BaseModel):
    email: EmailStr

class AuthResponse(BaseModel):
    access_token: str

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    code: str
