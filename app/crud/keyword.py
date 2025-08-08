from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.models.keyword import Keyword 

def get_or_create_keyword(db: Session, keyword_text: str):

    """
    Check if a keyword exists in the database.
    - If exists: return status=1 and its ID
    - If not: create it, return status=0 and the new ID
    - On error: return status=-1 with error message
    """

    try:
        # Check if keyword already exists
        existing_keyword = db.execute(
            select(Keyword).where(Keyword.value == keyword_text)
            ).scalar_one_or_none()

        if existing_keyword:
            return {
                "status": 1,  # Keyword exists
                "id": existing_keyword.id
            }
        
        for _ in range(2):
            try:
                # Create new keyword if not found
                new_keyword = Keyword(value=keyword_text)
                db.add(new_keyword)
                db.commit()
                db.refresh(new_keyword)

                return {
                    "status": 0, # Keyword created
                    "id": new_keyword.id
                }

            except SQLAlchemyError as e:
                # Rollback transaction on error
                db.rollback()
                return {
                    "status": -1, # Error occurred
                    "error": str(e)
                }
    except Exception as e:
        return {
            "status": -1, # Error occurred
            "error": str(e)
        }
