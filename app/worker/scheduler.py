from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import logging

logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Tehran"))

def start_scheduler():
    # for first time 
    scrap_job()
    
    scheduler.add_job(
        scrap_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_scraper_job",
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started at {datetime.now()}")
    print(f"[{datetime.now()}] Scheduler started!")

def shutdown_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler shutdown.")


def add_on_demand_job(keyword: str):
    job_id = f"on_demand_{keyword}_{datetime.now().timestamp()}"
    scheduler.add_job(
        scrap_job,
        args=[keyword],
        id=job_id,
        replace_existing=False,
    )
    logger.info(f"Added on-demand job for keyword '{keyword}' with ID {job_id}")
    print(f"On-demand job added for keyword '{keyword}'")

# for example
def scrap_job (keyword: str = None):
    if keyword:
        message = f"Scraping only for keyword: {keyword}"
    else:
        message = "Scraping for all keywords in DB"
    print(message)
    logger.info(message)