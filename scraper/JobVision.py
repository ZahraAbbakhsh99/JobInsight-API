from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import urllib.parse
import time
from typing import List, Dict
from app.schemas.job import JobBase
from app.utils.link_utils import normalize_job_link

BASE_URL = "https://jobvision.ir"

def scraping_JobVision(keyword: str) -> List[Dict[str, str]]:
    """
    Scrape job listings from JobVision.ir based on a keyword.

    Args:
        keyword (str): Search keyword for job titles.

    Returns:
        List[Dict[str, str]]: List of job dictionaries with title, salary, skills and link.
    """
    chrome_options = wd.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Selenium Chrome WebDriver
    driver = wd.Chrome(service=Service(ChromeDriverManager().install()),options=chrome_options)


    searched_url = BASE_URL + "/jobs/keyword/"
    encoded = urllib.parse.quote(keyword)

    all_jobs = []  # To store extracted job info
    page = 1

    try:
        while True:
            url = f"{searched_url}{encoded}?page={page}&sort=0"
            driver.get(url)
            time.sleep(1)

            try:
                WebDriverWait(driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.col-12.row.align-items-start")),
                        EC.presence_of_element_located((By.XPATH, "//h2[contains(text(),'فرصت شغلی برای جستجوی شما پیدا نشد')]"))
                    )
                )
            except :
                break
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, "a.col-12.row.align-items-start")

            # Stop if there are no job cards
            if not job_cards:
                break

            for card in job_cards:

                # Extract job title
                try:
                    title = card.find_element(By.CLASS_NAME, "job-card-title").text.strip()
                except:
                    title = None

                # Extract job link
                try:
                    link = card.get_attribute("href")
                    link = BASE_URL + link if link.startswith("/") else link
                except:
                    link = None

                # Skip if title or link is missing
                if not title or not link:
                    continue
                
                # Extract salary (optional)
                try:
                    salary_elements = card.find_elements(By.CSS_SELECTOR, "span.font-size-12px")
                    salary = salary_elements[-1].text.strip() if salary_elements else "نامشخص"
                    if not salary or "کارآموز" in salary or "امکان" in salary:
                        salary = "نامشخص"
                except:
                    salary = "نامشخص"

                # Add structured job info to result list
                all_jobs.append({
                    "title": title,
                    "salary": salary,
                    "link": normalize_job_link(link),
                })
            # Go to next page
            page += 1

        for job in all_jobs:

            # Open job detail page in a new tab to extract job requirements
            driver.get(job["link"])
            try:
                WebDriverWait(driver, 8).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.d-flex.bg-white.text-black")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.tag-title")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.tag.row"))
                    )
                )
            except:
                print(f"Timeout in job {job['link']}")
                job["skills"] = []
                continue
            
            skills = []

            # Extract required skills from job detail page
            spans1 = driver.find_elements(By.CSS_SELECTOR, "span.d-flex.bg-white.text-black.border")
            for sp in spans1:
                text = sp.text.strip()
                if text:
                    skills.append(text)

            job["skills"] = skills
                
    finally:
        # Close browser
        driver.quit()

    # keep only jobs that have non-empty 'skills' lists
    all_jobs = [job for job in all_jobs if "skills" in job and job["skills"]]
    
    # map scraped dicts -> ScrapedJob
    scraped_jobs: List[JobBase] = [
        JobBase(
            title=job["title"],
            salary=job.get("salary"),
            skills=job.get("skills"),
            link=job.get("link"),
        )
        for job in all_jobs
    ]
    return scraped_jobs
