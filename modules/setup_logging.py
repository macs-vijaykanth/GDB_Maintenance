import os
import logging
from datetime import datetime, timedelta
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def setup_logging():
    class LogColors:
        INFO = Fore.GREEN      # Green
        WARNING = Fore.YELLOW   # Yellow
        ERROR = Fore.RED       # Red
        CRITICAL = Fore.MAGENTA # Magenta
        DEBUG = Fore.BLUE # Blue
        RESET = Style.RESET_ALL # Reset to default

    # Custom logging formatter to add color for terminal output
    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            if record.levelno == logging.INFO:
                record.msg = f"{LogColors.INFO}{record.msg}{LogColors.RESET}"
            elif record.levelno == logging.WARNING:
                record.msg = f"{LogColors.WARNING}{record.msg}{LogColors.RESET}"
            elif record.levelno == logging.ERROR:
                record.msg = f"{LogColors.ERROR}{record.msg}{LogColors.RESET}"
            elif record.levelno == logging.DEBUG:
                record.msg = f"{LogColors.DEBUG}{record.msg}{LogColors.RESET}"  
            elif record.levelno == logging.CRITICAL:
                record.msg = f"{LogColors.CRITICAL}{record.msg}{LogColors.RESET}"
            return super().format(record)

    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels of logs

    # Create a log directory if it doesn't exist
    log_directory = "Logs"
    os.makedirs(log_directory, exist_ok=True)

    # Create file handler
    log_file_path  = os.path.join("Logs", datetime.now().strftime("logfile_%Y-%m-%d-%H-%M-%S.log"))
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)  # Log all levels to file

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Log all levels to console

    # Set formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    clean_old_logs(log_directory)

def clean_old_logs(log_directory):
    # Define the retention period (30 days)
    retention_period = timedelta(days=30)
    cutoff_time = datetime.now() - retention_period

    # Iterate through the log files in the directory
    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        # Check if the file is older than the retention period
        if os.path.isfile(file_path):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mod_time < cutoff_time:
                os.remove(file_path)  # Delete the old log file
                logging.info(f"Deleted old log file: {filename}")