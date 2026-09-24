from modules.setup_logging import setup_logging
from modules.gdbmaintenance import gdbmaintenance
from modules.send_email_notification import send_email_notification
from modules.get_secrets import get_secrets

def main():
    settings = get_secrets()  # Fetch and decode secrets from config.yaml
    setup_logging()  # Color-coded logging function
    gdbmaintenance(settings)  # Run export site operation for portal & all servers at the same time
    send_email_notification(settings)
    
if __name__ == '__main__':
    main()