from sqlalchemy.orm import Session
from app.models.keyword_queue import KeywordQueue
from datetime import datetime

def add_keyword_to_queue(db: Session, keyword: str, user_id: int = None):
    queue_item = KeywordQueue(keyword=keyword, user_id=user_id)
    db.add(queue_item)
    db.commit()
    db.refresh(queue_item)
    return queue_item.id

def get_pending_keywords(db: Session, limit: int = 10):
    items = db.query(KeywordQueue).filter(KeywordQueue.status=="pending").limit(limit).all()
    return items

def mark_keyword_done(db: Session, keyword_id: int):
    item = db.query(KeywordQueue).filter(KeywordQueue.id == keyword_id).first()
    if item:
        item.status = "done"
        item.processed_at = datetime.now()
        db.commit()
        return True
    return False