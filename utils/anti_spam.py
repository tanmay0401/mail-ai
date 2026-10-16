import time
import random
from datetime import datetime
import config
from utils.logger import log_info, log_warning

def wait_random_delay():
    """Waits for a random number of seconds between the configured min and max."""
    delay = random.uniform(config.DELAY_BETWEEN_EMAILS_MIN, config.DELAY_BETWEEN_EMAILS_MAX)
    log_info(f"Anti-spam: Waiting for {delay:.2f} seconds before next email...")
    time.sleep(delay)

def handle_batch_pause(emails_sent_in_batch):
    """Takes a longer pause after a certain number of emails to simulate human breaks."""
    if emails_sent_in_batch >= config.BATCH_SIZE:
        pause_minutes = random.uniform(config.PAUSE_AFTER_BATCH_MIN_MINUTES, config.PAUSE_AFTER_BATCH_MAX_MINUTES)
        log_info(f"Anti-spam: Batch size of {config.BATCH_SIZE} reached. Taking a break for {pause_minutes:.2f} minutes.")
        time.sleep(pause_minutes * 60)
        return 0 # Reset batch counter
    return emails_sent_in_batch

def is_within_business_hours():
    """Checks if the current local time is within business hours."""
    current_hour = datetime.now().hour
    return config.BUSINESS_HOURS_START <= current_hour < config.BUSINESS_HOURS_END

def enforce_business_hours():
    """Sleeps if it's currently outside of business hours."""
    while not is_within_business_hours():
        log_warning(f"Anti-spam: Outside business hours ({config.BUSINESS_HOURS_START}:00 - {config.BUSINESS_HOURS_END}:00). Sleeping for 30 minutes...")
        time.sleep(30 * 60)

def get_daily_limit(current_day):
    """Calculates the max emails allowed for today based on the warmup schedule."""
    for (start_day, end_day), limit in config.WARMUP_SCHEDULE.items():
        if start_day <= current_day <= end_day:
            return min(limit, config.ABSOLUTE_MAX_DAILY_SENDS)
    
    # Default fallback
    return 100
