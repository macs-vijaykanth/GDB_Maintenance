import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import logging
from datetime import datetime

def send_email_notification(settings):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
    logs_folder = os.path.join(parent_dir, "Logs")

    latest_log_file = None
    log_contents = ""

    try:
        if not os.path.exists(logs_folder):
            raise FileNotFoundError(f"Logs folder not found: {logs_folder}")

        # Get all .log files from Logs folder
        log_files = [
            os.path.join(logs_folder, f)
            for f in os.listdir(logs_folder)
            if f.endswith(".log")
        ]

        if not log_files:
            raise FileNotFoundError("No log files found in Logs folder.")

        # Get latest modified log file
        latest_log_file = max(log_files, key=os.path.getmtime)

        with open(latest_log_file, 'r') as log_file:
            log_contents = log_file.read()

        logging.info(f"Read latest log file: {latest_log_file}")

    except FileNotFoundError as e:
        logging.error(f"Log file not found: {e}")
        log_contents = "Could not read log file."
    except PermissionError as e:
        logging.error(f"Permission denied reading log file: {e}")
        log_contents = "Could not read log file due to permission error."
    except Exception as e:
        logging.error(f"Failed to read latest log file: {e}")
        log_contents = "Could not read log file."

    try:
        # Extract color-coded log messages from the log contents
        colored_logs = ""
        for line in log_contents.split('\n'):
            if "ERROR" in line:
                colored_logs += f"<span style='color: red;'>{line}</span><br>"
            elif "WARNING" in line:
                colored_logs += f"<span style='color: orange;'>{line}</span><br>"
            elif "INFO" in line:
                colored_logs += f"<span style='color: green;'>{line}</span><br>"

        # Prepare the email body with color-coded logs
        body = "<html><body>"
        body += colored_logs
        body += "</body></html>"

        msg = MIMEMultipart('mixed')
        msg['Subject'] = f"{settings.client_name} - GDB Maintenance"
        msg['From'] = settings.email.smtp_username
        msg['To'] = ', '.join(settings.email.email_recipients)
        msg.attach(MIMEText(body, "html"))

        # Attach the latest log file
        if latest_log_file and os.path.exists(latest_log_file):
            try:
                with open(latest_log_file, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(latest_log_file)}"'
                )
                msg.attach(part)
                logging.info(f"Attached log file: {os.path.basename(latest_log_file)}")
            except Exception as e:
                logging.error(f"Failed to attach log file: {e}")

        mail = smtplib.SMTP(settings.email.smtp_server, settings.email.smtp_port)
        mail.ehlo()
        mail.starttls()
        mail.login(settings.email.smtp_username, settings.email.smtp_password)
        mail.sendmail(msg['From'], settings.email.email_recipients, msg.as_string())
        mail.quit()
        logging.info("Email notification sent successfully")

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP authentication failed: {e}")
    except smtplib.SMTPConnectError as e:
        logging.error(f"Failed to connect to SMTP server: {e}")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")