from pydantic import BaseModel

class AuthRequest(BaseModel):
    email: str

class AuthResponse(BaseModel):
    access_token: str
