from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import List, Dict
from app.schemas.job import JobBase
from app.utils.link_utils import normalize_job_link

BASE_URL = "https://jobvision.ir"

def get_driver():
    chrome_options = wd.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return wd.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def fetch_job_skills(job):
    driver = get_driver()
    try:
        # Open job detail page in a new tab to extract job requirements
        driver.get(job["link"])
        WebDriverWait(driver, 5).until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.d-flex.bg-white.text-black.border")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.tag-title")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.tag.row"))
            )
        )
        skills = []
        # Extract required skills from job detail page
        spans = driver.find_elements(By.CSS_SELECTOR, "span.d-flex.bg-white.text-black.border")
        for sp in spans:
            txt = sp.text.strip()
            if txt:
                skills.append(txt)
        job["skills"] = skills
    except Exception as e:
        print(f"Error {job['link']}: {e}")
        job["skills"] = []
    finally:
        driver.quit()
    return job

def fetch_parallel(all_jobs, workers):
    
    def worker(sub_jobs):
        results = []
        for job in sub_jobs:
            results.append(fetch_job_skills(job))
        return results

    chunk_size = max(1, len(all_jobs) // workers)
    chunks = [all_jobs[i:i + chunk_size] for i in range(0, len(all_jobs), chunk_size)]

    results = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(worker, chunk) for chunk in chunks]
        for future in as_completed(futures):
            try:
                res = future.result()
                if res:
                    results.extend(res)
            except Exception as e:
                print(f"[Future error] {e}")

    return results

def scraping_JobVision(keyword: str) -> List[Dict[str, str]]:
    """
    Scrape job listings from JobVision.ir based on a keyword.

    Args:
        keyword (str): Search keyword for job titles.

    Returns:
        List[Dict[str, str]]: List of job dictionaries with title, salary, skills and link.
    """
    # Initialize Selenium Chrome WebDriver
    driver = get_driver()

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
        driver.quit()

        all_jobs = fetch_parallel(all_jobs, workers= 6)
                
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
