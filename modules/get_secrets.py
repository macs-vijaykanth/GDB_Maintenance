import base64
from dynaconf import Dynaconf
import logging

# Initialize Dynaconf with the path to your config.yaml
settings = Dynaconf(settings_files=['config.yaml'])

def get_secrets():
    logging.info("Starting the credentials fetching process for the application.")
    try:
        settings.email.smtp_username = base64.b64decode(settings.email.smtp_username).decode('utf-8')
        settings.email.smtp_password = base64.b64decode(settings.email.smtp_password).decode('utf-8')
        logging.info("Credentials were successfully decoded from Base64 values.")
    except Exception as e:
        logging.error(f"An error occurred while decoding Base64 values for credentials: {e}")
        return None
    return settings