import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- SMTP SETTINGS ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# --- RUN MODE ---
MODE = os.getenv("MODE", "dry-run").lower()
TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL_ADDRESS", "")
DATA_FILE = os.getenv("DATA_FILE", "data/example_leads.csv")

# --- LIMITING SETTINGS ---
MAX_COMPANIES_LIMIT = int(os.getenv("MAX_COMPANIES_LIMIT", "50"))
LIMIT_BY_UNIQUE_COMPANIES = os.getenv("LIMIT_BY_UNIQUE_COMPANIES", "True").lower() == "true"
EMAIL_ONLY_FIRST_CONTACT = os.getenv("EMAIL_ONLY_FIRST_CONTACT", "True").lower() == "true"

# --- WARMUP SCHEDULE ---
# Defines max emails per day based on the day of the campaign:
# Day 1-3: 25/day
# Day 4-7: 50/day
# Day 8-14: 100/day
# Day 15+: 200/day
WARMUP_SCHEDULE = {
    (1, 3): 25,
    (4, 7): 50,
    (8, 14): 100,
    (15, 999): 200
}
CURRENT_CAMPAIGN_DAY = int(os.getenv("CURRENT_CAMPAIGN_DAY", "1"))

# --- ANTI-SPAM SETTINGS ---
# Random delay between each email (in seconds)
DELAY_BETWEEN_EMAILS_MIN = float(os.getenv("DELAY_BETWEEN_EMAILS_MIN", "5"))
DELAY_BETWEEN_EMAILS_MAX = float(os.getenv("DELAY_BETWEEN_EMAILS_MAX", "15"))

# Long pause after sending a batch of emails
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))
PAUSE_AFTER_BATCH_MIN_MINUTES = float(os.getenv("PAUSE_AFTER_BATCH_MIN_MINUTES", "10"))
PAUSE_AFTER_BATCH_MAX_MINUTES = float(os.getenv("PAUSE_AFTER_BATCH_MAX_MINUTES", "20"))

# Business Hours (24-hour format in local time)
BUSINESS_HOURS_START = int(os.getenv("BUSINESS_HOURS_START", "9"))
BUSINESS_HOURS_END = int(os.getenv("BUSINESS_HOURS_END", "18"))

# Limit max daily sends as an absolute safety net
ABSOLUTE_MAX_DAILY_SENDS = int(os.getenv("ABSOLUTE_MAX_DAILY_SENDS", "500"))

# --- TEMPLATE & ATTACHMENT SETTINGS ---
TEMPLATES_DIR = os.getenv("TEMPLATES_DIR", "templates")
ATTACHMENT_PATH = os.getenv("ATTACHMENT_PATH", "")
