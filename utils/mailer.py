import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import config
from utils.logger import log_error, log_info

def create_smtp_connection():
    """Creates and returns an authenticated SMTP connection."""
    try:
        if config.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
        else:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
            server.starttls()
            
        server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
        return server
    except Exception as e:
        log_error(f"Failed to connect to SMTP server: {e}")
        return None

def send_email(server, to_email, subject, body_text, attachment_path=None):
    """Sends an email using an existing SMTP connection."""
    try:
        msg = MIMEMultipart()
        msg['From'] = config.EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach plain text body (HTML can be added here later if needed)
        msg.attach(MIMEText(body_text, 'plain'))

        # Handle attachment
        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)
            except Exception as e:
                log_error(f"Failed to attach file {attachment_path}: {e}")

        server.send_message(msg)
        return True, ""
    except Exception as e:
        error_msg = str(e)
        log_error(f"Failed to send email to {to_email}: {error_msg}")
        return False, error_msg
