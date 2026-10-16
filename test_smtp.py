"""
SMTP Connectivity Diagnostic Tool
Quickly verifies whether your SMTP credentials and connection settings work properly.
"""
import sys
from colorama import Fore, Style, init
import config
from utils.mailer import create_smtp_connection

init(autoreset=True)

def test_connection():
    print(f"\n{Fore.CYAN}=== Cold Email Bot: SMTP Diagnostics ==={Style.RESET_ALL}\n")
    print(f"Target Host: {config.SMTP_HOST}")
    print(f"Target Port: {config.SMTP_PORT}")
    print(f"Sender Email: {config.EMAIL_ADDRESS or '(Not configured)'}")
    
    if not config.EMAIL_ADDRESS or not config.EMAIL_PASSWORD:
        print(f"\n{Fore.RED}[ERROR] Missing EMAIL_ADDRESS or EMAIL_PASSWORD in .env file!{Style.RESET_ALL}")
        print("Please copy .env.example to .env and fill in your credentials.")
        return False
        
    print(f"\nConnecting to {config.SMTP_HOST}:{config.SMTP_PORT} and authenticating...")
    server = create_smtp_connection()
    
    if server:
        print(f"\n{Fore.GREEN}[SUCCESS] SMTP authentication succeeded! Your email server is ready to send.{Style.RESET_ALL}\n")
        try:
            server.quit()
        except Exception:
            pass
        return True
    else:
        print(f"\n{Fore.RED}[FAILED] Unable to authenticate with SMTP server.{Style.RESET_ALL}")
        print("\nCommon troubleshooting steps:")
        print("1. If using Gmail/Google Workspace, ensure 2-Step Verification is enabled.")
        print("2. Ensure you are using a 16-character App Password (not your account password).")
        print("   Generate one at: https://myaccount.google.com/apppasswords")
        print("3. Ensure SMTP_PORT is 465 (SSL) or 587 (TLS).")
        print("4. Check if your network or firewall is blocking outbound SMTP ports.\n")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
