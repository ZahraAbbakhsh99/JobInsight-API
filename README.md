# JobInsight-API

JobInsight API is a web scraping and data preparation service that collects structured data from online job advertisements.
It focuses on extracting key fields such as job titles, required skills, salary information, and posting links, and provides clean, ready-to-analyze datasets for future research and insights.


## Features

* Scrape job postings from multiple job boards
* Normalize and clean job data (title, salary, skills, link)
* Store scraped jobs in relational database (**PostgreSQL**)
* Daily and fallback scraping tasks using **APScheduler**
* On-demand scraping per keyword
* Email notification to users when jobs are processed
* Initial seeding of keywords

---

## Tech Stack

* **Python 3.10+**
* **FastAPI**
* **SQLAlchemy**
* **APScheduler**
* **PostgreSQL**
* **SMTP Email** integration

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ZahraAbbakhsh99/JobInsight-API.git
cd JOBINSIGHT-API
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```
---

## Browser Driver
This project uses Selenium for web scraping, 
which requires Google Chrome and ChromeDriver to be installed on your system. 

Follow these steps to set up ChromeDriver:

* 1. Install Google Chrome:

Ensure you have Google Chrome installed. Download it from https://www.google.com/chrome/ if you don't already have it.
Check your Chrome version by navigating to chrome://version in the browser.

* 2. Download ChromeDriver:

Visit the ChromeDriver download page: https://chromedriver.chromium.org/downloads.
Download the ChromeDriver version that matches your installed Chrome version.
Extract the downloaded chromedriver executable.

* 3. Add ChromeDriver to PATH:

Move the chromedriver executable to a directory included in your system's PATH, such as:

Linux/Mac: /usr/local/bin/ or /usr/bin/
Windows: C:\Program Files\ChromeDriver\ or any directory in your PATH.

* 4. Automate ChromeDriver Installation:
```bash
pip install webdriver-manager
```

## Environment Variables

To run this project, create a `.env` file in the root directory.
You can copy the provided `.env.example` file:

```bash
cp .env.example .env
```

Fill in your own values:

| Variable             | Description                                                               |
| -------------------- | ------------------------------------------------------------------------- |
| `DEBUG`              | Enable/disable debug mode (`True` / `False`)                              |
| **SMTP (Email)**     |                                                                           |
| `SMTP_HOST`          | SMTP server host (e.g., `smtp.gmail.com`)                                 |
| `SMTP_PORT`          | SMTP server port (e.g., `587`)                                            |
| `SMTP_USER`          | Your email address (used for sending emails)                              |
| `SMTP_PASS`          | Your email app password (Google App Password) |
| `FROM_EMAIL`         | Sender email address                                                      |
| **JWT / Auth**       |                                                                           |
| `JWT_SECRET`         | A strong secret key for JWT token signing                                 |
| `JWT_ALGORITHM`      | Algorithm used for JWT (default: `HS256`)                                 |
| `TOKEN_EXPIRE_HOURS` | Expiration time for JWT tokens (in hours)                                 |
| `OTP_EXPIRE_MINUTES` | Expiration time for OTP codes (in minutes)                                |
| **Database**         |                                                                           |
| `POSTGRES_USER`      | PostgreSQL username                                                       |
| `POSTGRES_PASSWORD`  | PostgreSQL password                                                       |
| `POSTGRES_DB`        | Database name (default: `jobinsight`)                                     |
| `POSTGRES_HOST`      | Database host (default: `localhost`)                                      |
| `POSTGRES_PORT`      | Database port (default: `5432`)                                           |

---

## Database Setup

Make sure PostgreSQL is installed and running.
Create the database:

```bash
createdb jobinsight
```
---

## Running the Application

Run with FastAPI CLI:

```bash
fastapi dev main.py
```

The API will be available at:

```
http://127.0.0.1:8000
```

API docs:

```
http://127.0.0.1:8000/docs
```
