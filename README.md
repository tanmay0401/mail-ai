# Mail AI - Cold Email Automation Engine

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/CI-Passing-brightgreen.svg)]()
[![SMTP Tested](https://img.shields.io/badge/SMTP-Gmail%20%7C%20Outlook%20%7C%20Custom-blue.svg)]()

A production-ready, highly deliverable cold email automation system designed for professionals, founders, researchers, and students conducting outreach at scale without landing in spam.

---

## Key Features

- **Dynamic Spreadsheet Templating**: Supports both **CSV** and multi-sheet **Excel (.xlsx, .xls)**. Auto-detects headers and injects custom fields (e.g. `{first_name}`, `{company}`, `{role}`, `{notes}`) into your templates.
- **Deliverability & Anti-Spam Engine**:
  - Configurable random delays between individual sends.
  - Periodic batch pauses simulating human breaks.
  - Business-hours enforcement to only send during target operating windows.
  - Built-in campaign warmup schedule to safely scale sending volume.
- **Dynamic Template Rotation**: Automatically selects and rotates across multiple `.txt` email templates in `templates/` to avoid repetitive-pattern spam filters.
- **Fail-Safe Resume System**: Tracks delivery state per row (`SUCCESS` / `FAILED` with timestamps). If interrupted, simply re-run: it automatically picks up where it left off without re-emailing anyone.
- **Multi-Phase Testing Pipeline**:
  - `dry-run`: Renders and prints complete personalized emails to console without sending anything.
  - `test`: Connects to SMTP and sends a single diagnostic test email to your personal test address.
  - `live`: Runs outreach to your leads database with deliverability delays.
- **Multi-Sheet Lead Extractor**: Includes `extract_emails.py` CLI utility to aggregate, clean, deduplicate, and export leads from multi-tab Excel workbooks into clean CSVs.
- **Optional File Attachments**: Attach resumes, portfolios, or pitch decks automatically via environment configuration.

---

## Project Structure

```text
mail-ai/
├── data/
│   └── example_leads.csv       # Sample leads dataset (customizable)
├── templates/
│   ├── template1.txt          # Job & internship outreach template
│   ├── template2.txt          # Professional networking template
│   └── template3.txt          # Business & collaboration template
├── utils/
│   ├── anti_spam.py           # Delay jitter, batching, and business-hour limits
│   ├── logger.py              # Colored terminal output & daily file logging
│   ├── mailer.py              # Authenticated SMTP connection and MIME builder
│   ├── processor.py           # First name extractor and template personalizer
│   └── spreadsheet.py         # CSV & Excel parser with auto-header detection
├── tests/                     # Automated unit test suite
│   ├── test_config.py
│   └── test_processor.py
├── .env.example               # Configuration template
├── .gitignore                 # Pre-configured to prevent leaking credentials/CVs
├── config.py                  # Central configuration module
├── extract_emails.py          # Multi-sheet Excel contact extractor utility
├── main.py                    # Main campaign orchestrator
├── requirements.txt           # Python package dependencies
├── test_smtp.py               # SMTP connectivity diagnostic tool
└── README.md
```

---

## 5-Minute Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/tanmay0401/mail-ai.git
cd mail-ai
```

### 2. Create and Activate Virtual Environment
```bash
# macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt / PowerShell):
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Environment (`.env`)
Copy `.env.example` to `.env`:
```bash
# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

Open `.env` in any text editor and fill in your email credentials.

---

## Setting Up Your Email Credentials

### For Google Workspace / Gmail (Recommended)
Google requires an **App Password** for SMTP automation (your regular Gmail password will NOT work):
1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
2. Enable **2-Step Verification** (if not already enabled).
3. Search for or navigate to [App Passwords](https://myaccount.google.com/apppasswords).
4. Enter an app name (e.g. `Mail AI`) and click **Create**.
5. Copy the generated 16-character password into `.env`:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=465
   EMAIL_ADDRESS=your.name@gmail.com
   EMAIL_PASSWORD=xxxx xxxx xxxx xxxx
   ```

### For Outlook / Office 365
```env
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_ADDRESS=your.email@outlook.com
EMAIL_PASSWORD=your_password
```

---

## Verify Your Connection

Run the diagnostic tool to verify that your credentials and SMTP host can authenticate:
```bash
python test_smtp.py
```
If successful, you will see `[SUCCESS] SMTP authentication succeeded!`.

---

## Data & Template Customization

### 1. Preparing Your Leads (`data/example_leads.csv` or `.xlsx`)
Place your contacts into `data/` or reference any CSV/Excel file in `.env`:
```env
DATA_FILE=data/example_leads.csv
```
Supported columns (auto-detected):
- `email` or `email address` / `mail`
- `full_name` or `name` / `contact name`
- `company` or `company name` / `organization`
- Any custom column (e.g., `role`, `linkedin`, `notes`)

### 2. Crafting Email Templates (`templates/`)
Any `.txt` file added to the `templates/` folder is automatically loaded.
- The **first line** must specify the subject line: `Subject: Your Subject Here`
- The rest of the file forms the email body.
- Available placeholders:
  - `{first_name}`: Automatically extracted from `full_name` (or derived from email username).
  - `{company}`: Recipient's organization.
  - `{role}`: Recipient's title.
  - `{custom_column}`: Any column present in your spreadsheet.

Example (`templates/my_outreach.txt`):
```text
Subject: Exploring synergy with {company}

Hi {first_name},

I noticed your recent work at {company} as {role} and wanted to reach out.

[Your personalized message here...]

Best regards,
Your Name
```

---

## Running Campaigns

### Step 1: Dry-Run Mode (Safe Preview)
Verify that your templates render with your leads without sending any real emails:
```bash
# In .env: MODE=dry-run
python main.py
```

### Step 2: Test Mode
Sends a single live email to `TEST_EMAIL_ADDRESS` specified in `.env` so you can inspect formatting and spam filters directly in an inbox:
```bash
# In .env: MODE=test
python main.py
```

### Step 3: Live Mode
When ready to begin outreach:
```bash
# In .env: MODE=live
python main.py
```
> The script saves delivery status after every single email. You can safely close terminal or stop the script anytime (`Ctrl+C`) and re-run whenever you want—already-contacted leads will never be messaged twice.

---

## Utility: Extracting Leads from Multi-Sheet Excel Files

If you have a multi-sheet spreadsheet with prospects across various tabs:
```bash
python extract_emails.py path/to/workbook.xlsx data/cleaned_leads.csv
```
This utility:
- Scans all sheets in the workbook.
- Auto-detects header offsets (rows 1-10).
- Normalizes column names.
- Filters invalid or missing emails and removes duplicates.

---

## Deliverability Best Practices

1. **Warmup New Inboxes**: Do not send 300+ emails on a fresh domain. Start with 20-30/day, gradually increasing by 20% weekly.
2. **Personalize Every Email**: Keep emails plain text (higher inbox placement than HTML) and reference specific details using `{first_name}` and `{company}`.
3. **Pacing**: Use the built-in `DELAY_BETWEEN_EMAILS_MIN` (e.g. 10s) and `DELAY_BETWEEN_EMAILS_MAX` (e.g. 25s) to avoid triggering provider velocity alerts.
4. **Attachments**: If attaching documents via `ATTACHMENT_PATH`, keep file size under 2MB.

---

## Running Unit Tests

Run the built-in automated test suite:
```bash
python -m unittest discover -s tests
```

---

## License

This project is licensed under the [MIT License](LICENSE).
