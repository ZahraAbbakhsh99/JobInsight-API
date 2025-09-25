from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from typing import List, Dict
import urllib.parse
import time
from app.schemas.job import JobBase
from app.utils.link_utils import normalize_job_link
from app.utils.text_utils import clean_text

BASE_URL = "https://karbord.io/jobs"

def scraping_Karbord(keyword: str) -> List[Dict[str, str]]:
    """
    Scrape job listings from Karbord.io based on a keyword.

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
    driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    encoded = urllib.parse.quote(keyword)
    all_jobs = []  # To store extracted job info
    page = 1

    try:
        while True: 
            url = f"{BASE_URL}?keyword={encoded}&page={page}&sort=0"
            driver.get(url)
            time.sleep(1)
            try:
                WebDriverWait(driver, 5).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.job-card, app-jobs-empty-state"))
                    )
                empty_state = driver.find_elements(By.CSS_SELECTOR, "app-jobs-empty-state")
                
                # Stop if there are no job cards
                if empty_state:
                    break
            except TimeoutException:
                print("Timeout")
                break
           
            job_cards = driver.find_elements(By.CSS_SELECTOR, "a.job-card")
            if not job_cards:
                break

            # Extract job info from each card
            for job in job_cards:
                # Job title
                try:
                    title = clean_text(job.find_element(By.CSS_SELECTOR, "h4").text.strip())
                except:
                    title = None

                # Job link
                try:
                    job_id = job.get_attribute("id").replace("el-", "")
                    link = f"https://karbord.io/jobs/detail/{job_id}"
                    link = normalize_job_link(link)
                except:
                    link = None

                if not title or not link:
                    continue

                # Job salary (optional)
                try:
                    spans = job.find_elements(By.XPATH, ".//span[contains(text(),'تومان')]")
                    salary = spans[0].text.strip() if spans else "نامشخص"
                except:
                    salary = "نامشخص"

                # Append job to results list
                all_jobs.append({
                    "title": title,
                    "salary": salary if salary else "نامشخص",
                    "link": link
                })
            # Go to next page
            page += 1

        for job in all_jobs:
            # Open job detail page
            driver.get(job["link"])

            # Wait for the entire container that includes all job conditions
            try:
                WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job-specification__condition-value"))
                )
            except TimeoutException:
                job["skills"] = []
                continue

            skills = []
            # Extract skills
            try:
                li_tags = driver.find_elements(By.CSS_SELECTOR, "li.tag")
                for li in li_tags:
                    skill = li.text.strip()
                    if skill:
                        skills.append(skill)

                software_tags = driver.find_elements(
                By.CSS_SELECTOR, "app-tag.tag.job-specification__condition-value__tag"
                )
                for tag in software_tags:
                    parts = tag.text.strip().split("|")
                    if len(parts) == 2:
                        skill, level = parts[0].strip(), parts[1].strip()
                        skills.append(f"{skill} ({level})")
                    elif parts:
                        skills.append(parts[0].strip())
            
            except Exception as e :
                job["skills"] = None 
                
            job["skills"] = skills
            
        # keep only jobs that have non-empty 'skills' lists
        all_jobs = [job for job in all_jobs if job.get("skills")]
    finally:
        # Close browser
        driver.quit()

    # map scraped dicts -> ScrapedJob
    scraped_jobs: List[JobBase] = [
        JobBase(
            title=job["title"],
            salary=job.get("salary"),
            skills=job.get("skills", ["نامشخص"]),
            link=job.get("link"),
        )
        for job in all_jobs
    ]

    return scraped_jobs
