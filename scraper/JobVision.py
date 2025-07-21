from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import List, Dict

def scraping_JobVision(keyword: str, max_jobs: int = 15) -> List[Dict[str, str]]:
    """
    Scrape job listings from JobVision.ir based on a keyword.

    Args:
        keyword (str): Search keyword for job titles.
        max_jobs (int): Maximum number of job listings to return.

    Returns:
        List[Dict[str, str]]: List of job dictionaries with title, salary, requirements and link.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Selenium Chrome WebDriver
    driver = wd.Chrome(options=chrome_options)

    base_url = "https://jobvision.ir/jobs/keyword/"
    all_jobs = []
    page = 1

    try:
        # Keep scraping until collect max_jobs
        while len(all_jobs) < max_jobs:
            url = f"{base_url}{keyword}?page={page}&sort=1"
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "job-card-title"))
            )

            # Parse page source using BeautifulSoup
            soup = bs(driver.page_source, "html.parser")
            job_cards = soup.find_all("job-card", class_="col-12")

            # Stop if there are no job cards
            if not job_cards:
                break

            for card in job_cards:
                if len(all_jobs) >= max_jobs:
                    break
                
                # Extract job title
                title_tag = card.select_one("div.job-card-title")
                title = title_tag.text.strip() if title_tag else None

                # Extract job link
                link_tag = card.find("a", href=True)
                link = "https://jobvision.ir" + link_tag["href"] if link_tag else None

                # Skip if title or link is missing
                if not title or not link:
                    continue
                
                # Extract salary (optional)
                salary_tag = card.select_one("span.font-size-12px")
                salary = salary_tag.text.strip() if salary_tag else "نامشخص"

                # Open job detail page in a new tab to extract job requirements
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)

                time.sleep(3)
                job_soup = bs(driver.page_source, "html.parser")

                # Extract required skills from job detail page
                skill_tags = job_soup.find_all(
                    "span",
                    class_="d-flex bg-white text-black border border-secondary col rounded-sm text-white"
                )
                # requirements = ", ".join(tag.text.strip() for tag in skill_tags) if skill_tags else "نامشخص"

                if skill_tags:
                    requirements = [tag.text.strip() for tag in skill_tags]
                else:
                    requirements = ["نامشخص"]
                
                # Close job detail tab and switch back to main tab
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # Add structured job info to result list
                all_jobs.append({
                    "title": title,
                    "salary": salary,
                    "requirements": requirements,
                    "link": link
                })

            # Go to next page if needed
            page += 1

    finally:
        # Close browser
        driver.quit()

    return all_jobs
