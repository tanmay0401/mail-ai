import logging
import os
import colorama
from colorama import Fore, Style
from datetime import datetime

# Initialize colorama for Windows terminal support
colorama.init()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Generate a log filename with current date
log_filename = f"logs/campaign_{datetime.now().strftime('%Y-%m-%d')}.txt"

# Configure root logger
logger = logging.getLogger("ColdEmailBot")
logger.setLevel(logging.INFO)

# Create file handler
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Add handler to logger
logger.addHandler(file_handler)

def log_info(message):
    print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")
    logger.info(message)

def log_success(message):
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
    logger.info(f"SUCCESS: {message}")

def log_error(message):
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")
    logger.error(message)

def log_warning(message):
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
    logger.warning(message)
