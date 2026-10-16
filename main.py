"""
Mail AI: Cold Email Automation Orchestrator
Production-ready cold email sender with anti-spam delays, batch pausing,
smart name extraction, dynamic template rotation, and resume capabilities.
"""
import os
import random
import argparse
from datetime import datetime
import sys
from colorama import Fore, Style, init

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

init(autoreset=True)

import config
from utils import spreadsheet, processor, mailer, anti_spam
from utils.logger import log_info, log_success, log_error, log_warning

def load_templates():
    """Loads all templates (.txt files) from the configured templates directory."""
    templates = []
    if not os.path.exists(config.TEMPLATES_DIR):
        log_error(f"Templates directory '{config.TEMPLATES_DIR}' not found.")
        return templates

    for filename in sorted(os.listdir(config.TEMPLATES_DIR)):
        if filename.endswith(".txt") and not filename.endswith(".local"):
            filepath = os.path.join(config.TEMPLATES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        templates.append(content)
            except Exception as e:
                log_error(f"Error reading template {filename}: {e}")

    if not templates:
        log_warning("No templates found in the templates directory.")

    return templates

def parse_template(template_content):
    """Splits a template file into subject and body based on the first line."""
    lines = template_content.strip().split('\n')
    subject = "Connecting regarding opportunities"  # Default fallback
    body = template_content

    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0][8:].strip()
        body = '\n'.join(lines[1:]).strip()

    return subject, body

def run_campaign():
    """Main function to run the cold email campaign."""
    print(f"\n{Fore.CYAN}===================================================={Style.RESET_ALL}")
    print(f"{Fore.GREEN}              MAIL AI: CAMPAIGN LAUNCHER             {Style.RESET_ALL}")
    print(f"{Fore.CYAN}===================================================={Style.RESET_ALL}")
    log_info(f"Execution Mode: [{config.MODE.upper()}]")
    log_info(f"Target Dataset: {config.DATA_FILE}")

    # Display attachment info
    if config.ATTACHMENT_PATH:
        if os.path.exists(config.ATTACHMENT_PATH):
            log_info(f"Attachment: {config.ATTACHMENT_PATH} (Verified)")
        else:
            log_warning(f"Attachment specified ({config.ATTACHMENT_PATH}) but file not found on disk!")
    else:
        log_info("Attachment: (None configured)")

    # Check business hours enforcement in live mode
    if config.MODE == 'live':
        anti_spam.enforce_business_hours()

    # Calculate daily sending limit
    daily_limit = anti_spam.get_daily_limit(config.CURRENT_CAMPAIGN_DAY)
    if config.MODE == 'test':
        daily_limit = 1
        log_info("TEST MODE: Limiting run to exactly 1 email to test inbox rendering.")
    elif config.MODE == 'dry-run':
        log_info(f"DRY RUN MODE: Simulating execution (Safe preview, no emails sent).")
    else:
        log_info(f"Daily limit for Day {config.CURRENT_CAMPAIGN_DAY}: {daily_limit} emails.")

    # Load data
    df = spreadsheet.load_data(config.DATA_FILE)
    if df is None:
        log_error("Could not load dataset. Please check DATA_FILE path.")
        return

    pending_leads = spreadsheet.get_pending_leads(df)
    log_info(f"Found {len(pending_leads)} pending leads to process.")

    if len(pending_leads) == 0:
        log_info("No pending leads found to email. Campaign is up-to-date!")
        return

    # Load email templates
    templates = load_templates()
    if not templates:
        log_error("Aborting: No valid templates found in templates folder.")
        return
    log_info(f"Loaded {len(templates)} email template(s) for rotation.")

    # Count emails already sent today
    today_str = datetime.now().strftime("%Y-%m-%d")
    emails_sent_today = 0
    if 'sent_status' in df.columns and 'sent_time' in df.columns:
        sent_today = df[(df['sent_status'] == 'SUCCESS') & (df['sent_time'].astype(str).str.startswith(today_str))]
        emails_sent_today = len(sent_today)
        log_info(f"Already sent {emails_sent_today} email(s) today according to dataset log.")

    emails_sent_in_batch = 0

    # Connect to SMTP server if not in dry-run mode
    server = None
    if config.MODE != 'dry-run':
        server = mailer.create_smtp_connection()
        if not server:
            log_error("Failed to connect to SMTP server. Verify your credentials in .env.")
            return

    attachment_to_send = config.ATTACHMENT_PATH if (config.ATTACHMENT_PATH and os.path.exists(config.ATTACHMENT_PATH)) else None

    try:
        for index, row in pending_leads.iterrows():
            if emails_sent_today >= daily_limit:
                log_warning("Daily sending quota reached. Stopping campaign for today.")
                break

            first_name = processor.get_first_name(row)
            email = str(row.get('email', '')).strip().rstrip(',').strip()
            if ',' in email:
                parts = [p.strip() for p in email.split(',') if p.strip()]
                email = parts[0] if parts else email

            # Select and render personalized template
            raw_template = random.choice(templates)
            personalized_content = processor.personalize_template(raw_template, row)
            subject, body = parse_template(personalized_content)

            print(f"\n{Fore.MAGENTA}[{emails_sent_today + 1}/{daily_limit}]{Style.RESET_ALL} Preparing email for {first_name} <{email}>...")

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success = False
            error_msg = ""

            if config.MODE == 'dry-run':
                print(f"{Fore.YELLOW}--- DRY RUN: WOULD SEND ---{Style.RESET_ALL}")
                print(f"Recipient:  {email}")
                print(f"Subject:    {subject}")
                print(f"Attachment: {attachment_to_send or '(None)'}")
                print(f"Body Preview:\n{body[:120]}...\n---------------------------")
                success = True

            elif config.MODE == 'test':
                test_email = config.TEST_EMAIL_ADDRESS
                if not test_email:
                    log_error("TEST_EMAIL_ADDRESS is not set in .env! Cannot proceed in test mode.")
                    break
                log_info(f"TEST MODE: Routing email destined for {email} to {test_email}")
                success, error_msg = mailer.send_email(
                    server,
                    test_email,
                    f"[TEST for {email}] {subject}",
                    body,
                    attachment_to_send
                )

            else:  # live mode
                success, error_msg = mailer.send_email(
                    server,
                    email,
                    subject,
                    body,
                    attachment_to_send
                )
                if not success and any(term in error_msg.lower() for term in ["disconnect", "connection", "broken", "closed", "reset", "socket"]):
                    log_warning("SMTP connection lost. Attempting automatic reconnection...")
                    try:
                        server.quit()
                    except Exception:
                        pass
                    server = mailer.create_smtp_connection()
                    if server:
                        success, error_msg = mailer.send_email(
                            server,
                            email,
                            subject,
                            body,
                            attachment_to_send
                        )

            if success:
                log_success(f"Email successfully processed for {email}")
                if config.MODE == 'live':
                    spreadsheet.update_row_status(df, index, "SUCCESS", timestamp)
                emails_sent_today += 1
                emails_sent_in_batch += 1

                # Apply anti-spam delays during live sending
                if config.MODE == 'live' and emails_sent_today < len(pending_leads) and emails_sent_today < daily_limit:
                    anti_spam.wait_random_delay()
                    emails_sent_in_batch = anti_spam.handle_batch_pause(emails_sent_in_batch)
            else:
                if config.MODE == 'live':
                    spreadsheet.update_row_status(df, index, "FAILED", timestamp, error_msg)

            # Persist dataset after every send so progress is never lost
            if config.MODE == 'live':
                spreadsheet.save_data(df, config.DATA_FILE)

    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass

    log_info("Campaign run completed.")

if __name__ == "__main__":
    run_campaign()
