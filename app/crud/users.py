from sqlalchemy.orm import Session
from app.models.users import User

def get_user_email(db: Session, user_id: int) -> str:
    """
    Return the email of a user given the user_id.
    Raises ValueError if user not found.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} not found")
    return user.email
