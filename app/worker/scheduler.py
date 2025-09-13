from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import logging

from sqlalchemy.orm import Session

from database.session import get_db
from app.crud.queue import get_pending_keywords, mark_keyword_done
from app.crud.users import get_user_email
from app.utils.email_utils import send_email_async

# logging setup
logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# initialize scheduler with Tehran timezone
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Tehran"))

# add an on-demand job to the scheduler
def add_on_demand_job(keyword: str):
    job_id = f"on_demand_{keyword}_{datetime.now().timestamp()}"
    scheduler.add_job(
        on_demand_job,
        args=[keyword],
        id=job_id,
        replace_existing=False,
    )
    logger.info(f"Added on-demand job for keyword '{keyword}' with ID {job_id}")
    print(f"On-demand job added for keyword '{keyword}'")

# process a single keyword item from queue
def process_keyword(db: Session, keyword_item):
    """
    Process a single keyword and send email notification if user_id exists.
    """
    logger.info(f"Processing keyword: {keyword_item.keyword}")

    # run the actual scraper
    scrap_job(keyword_item.keyword)

    # mark the keyword as done in queue
    mark_keyword_done(db, keyword_item.id)
    if keyword_item.user_id:
        user_email = get_user_email(db, keyword_item.user_id)
        send_email_async(
            user_email,
            "Keyword Processed",
            f"Your keyword '{keyword_item.keyword}' has been processed. Your CSV is ready."
        )
        logger.info(f"Notification email sent to {user_email}")

# process a batch of pending keywords
def process_pending_keywords(db: Session, limit: int = 10):
    """
    Fetch pending keywords from the queue and process each one.
    """
    pending_items = get_pending_keywords(db, limit)
    for item in pending_items:
        process_keyword(db, item)

# daily job (runs every day at 2 AM)
def daily_job():
    logger.info("Starting daily job")
    with Session(get_db().bind) as db:
        process_pending_keywords(db, limit=20)  # process first 20 items
    logger.info("Daily job finished")

# fallback job (runs every 3 days at 5 AM)
def fallback_job():
    logger.info("Starting fallback job")
    with Session(get_db().bind) as db:
        process_pending_keywords(db, limit=50)  # process larger batch
    logger.info("Fallback job finished")

# On-demand job for a specific keyword
def on_demand_job(keyword: str):
    logger.info(f"Starting on-demand job for keyword: {keyword}")
    with Session(get_db().bind) as db:
        pending_items = get_pending_keywords(db)
        for item in pending_items:
            if item.keyword == keyword:
                process_keyword(db, item)
                break
    logger.info(f"On-demand job for '{keyword}' finished")

# start the scheduler
def start_scheduler():
    """
    Schedule daily and fallback jobs, and optionally run an initial batch.
    """
    scrap_job()
    
    # daily job at 2 AM
    scheduler.add_job(
        daily_job,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_scraper_job",
        replace_existing=True
    )

    # fallback job every 3 days at 5 AM
    scheduler.add_job(
        fallback_job,
        trigger=CronTrigger(day='*/3', hour=5, minute=0),
        id="fallback_scraper_job",
        replace_existing=True
    )
    logger.info("Fallback scraper job scheduled every 3 days at 5 AM")

    scheduler.start()
    logger.info(f"Scheduler started at {datetime.now()}")
    print(f"[{datetime.now()}] Scheduler started!")

# shutdown scheduler
def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler shutdown.")


# for example
def scrap_job (keyword: str = None):
    if keyword:
        message = f"Scraping only for keyword: {keyword}"
    else:
        message = "Scraping for all keywords in DB"
    print(message)
    logger.info(message)