import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

def send_failure_email(settings, error_message, operation):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"{settings.client_name} - GDB Maintenance - Failure"
    msg['From'] = settings.email.smtp_username
    msg['To'] = ', '.join(settings.email.email_recipients)
    body = f"""
    <html>
        <body>
            <span style='color: black; font-weight: bold;'>{operation}</span><br>
            <span style='color: red;'>{error_message}</span>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, "html"))
    mail = smtplib.SMTP(settings.email.smtp_server, settings.email.smtp_port)
    mail.connect(settings.email.smtp_server, settings.email.smtp_port)
    mail.ehlo()
    mail.starttls()
    mail.login(settings.email.smtp_username, settings.email.smtp_password)
    mail.sendmail(msg['From'], settings.email.email_recipients, msg.as_string())
    mail.quit()
    logging.error(f"Failure email sent for operation: {operation}")