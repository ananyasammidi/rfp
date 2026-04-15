# Restaurant RFP Automation System

End-to-end pipeline that scrapes a restaurant menu, extracts ingredients, prices them via USDA data, finds local distributors, and sends RFP emails.

**Restaurant:** [Ruby's Cafe — Soho](https://www.rubyscafe.com/soho-menu/#all-day)

---

## Stack

Language: Python
Framework: FastAPI
Database: SQLite (WAL mode)
Scraping: httpx + BeautifulSoup
Ingredient extraction: Comma-split descriptions + alias normalization
Pricing: USDA FoodData Central API
Distributors: Static list of NYC distributors
Email: Gmail SMTP

---

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

Open **http://localhost:8000** — paste any menu URL and click Run.

---

## Email setup

Go to **https://myaccount.google.com/apppasswords**, generate an App Password, and add to `.env`:

```
GMAIL_USER=you@gmail.com
GMAIL_APP_PASS=your16charpassword
```

Without this the pipeline saves emails but not not send them.
