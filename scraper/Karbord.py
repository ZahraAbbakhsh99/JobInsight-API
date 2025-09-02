from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict
import time
from app.schemas.scrape import ScrapedJob
from app.utils.link_utils import normalize_job_link


def scraping_Karbord(keyword: str, max_jobs: int = 10) -> List[Dict]:
    """
    Scrape job listings from Karbord.io based on a keyword.

    Args:
        keyword (str): Search keyword for job titles.
        max_jobs (int): Maximum number of job listings to return.

    Returns:
        List[Dict[str, str]]: List of job dictionaries with title, salary, requirements and link.
    """
    options = Options()
    options.add_argument("--headless")
    
    # Initialize Selenium Chrome WebDriver
    driver = webdriver.Chrome(options=options, service=Service())

    jobs = []  # To store extracted job info

    try:
        # Go to the homepage
        driver.get("https://karbord.io/")

        # Wait until the search input is loaded
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[placeholder="چه شغلی؟"]')
        ))

        # Enter the keyword in the search input
        search_input.send_keys(keyword)

        # Click the "Search" button
        search_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        search_button.click()

        # Wait for job cards to load
        job_cards = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'a.job-card')
        ))

        # Extract job info from each card
        for job in job_cards:
            try:

                # Job title
                try:
                    title = job.find_element(By.CSS_SELECTOR, 'h4.heading-01').text.strip()
                except:
                    title = "نامشخص"
                    continue

                # Job link
                try:
                    el_id = job.get_attribute("id")
                    if el_id and el_id.startswith("el-"):
                        job_id = el_id.replace("el-", "")
                        link = f"https://karbord.io/jobs/detail/{job_id}"
                except:
                    link = "نامشخص"
                    continue

                # Job salary
                salary = "نامشخص"
                salary_icon = job.find_elements(By.CSS_SELECTOR, 'img[alt="salary"]')
                if salary_icon:
                    salary_span = job.find_elements(By.CSS_SELECTOR, 'span.body-short-01')
                    for s in salary_span:
                        if "تومان" in s.text:
                            salary = s.text.strip()
                            break

                # Open job detail page
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)

                skills = []

                try:
                    # Wait for the entire container that includes all job conditions
                    WebDriverWait(driver, 8).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.job-specification__condition-value'))
                    )

                    # Find the parent <div> that has <label> "نرم افزارها"
                    skill_div = None
                    containers = driver.find_elements(By.CSS_SELECTOR, 'div.mx-6.border-t.py-4')
                    for div in containers:
                        try:
                            label = div.find_element(By.CSS_SELECTOR, 'label').text.strip()
                            if label == "نرم افزارها":
                                skill_div = div
                                break
                        except:
                            continue

                    # Extract skill name and level
                    if skill_div:
                        tags = skill_div.find_elements(By.CSS_SELECTOR, 'app-tag')
                        for tag in tags:
                            parts = tag.text.strip().split("|")
                            skill = parts[0].strip()
                            level = parts[1].strip() if len(parts) > 1 else "نامشخص"
                            skills.append(f"{skill} | {level}")

                except Exception as e:
                    print(f"Error loading app-tag skills: {e}")

                # Extract skills from <li class='tag'> elements
                try:
                    li_tags = driver.find_elements(By.CSS_SELECTOR, 'li.tag')
                    for li in li_tags:
                        text = li.text.strip()
                        if text and text not in [s.split("|")[0].strip() for s in skills]:
                            skills.append(f"{text}")
                except Exception as e:
                    print(f"Error loading li.tag skills: {e}")

                if not skills:
                    print(f"No skills found for job {job_id}, skipping.")
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue

                # Append job to results list
                jobs.append({
                    "title": title,
                    "salary": salary,
                    "requirements": skills,
                    "link": link,
                })

                if len(jobs) >= max_jobs:
                    break

                # Close job tab and go back to main
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1.5)

                # map scraped dicts -> ScrapedJob
                scraped_jobs: List[ScrapedJob] = [
                    ScrapedJob(
                        title=job["title"],
                        salary=job.get("salary"),
                        requirements=job.get("requirements", ["نامشخص"]),
                        link=normalize_job_link(job["link"])
                    )
                    for job in jobs
                ]


            except Exception as e:
                print(f"Error processing a job: {e}")
                continue

    finally:
        driver.quit()

    return scraped_jobs
    