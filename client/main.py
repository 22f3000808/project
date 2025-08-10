import argparse
import time
import platform
import requests
from datetime import datetime, timezone

import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()



from utils import (
    get_machine_id,
    load_last_report,
    save_last_report,
    has_changed,
    logger,
)
from checks import (
    check_disk_encryption,
    check_os_updates,
    check_antivirus,
    check_sleep_setting,
)

SERVER_URL = "http://localhost:8000/api/v1/report"  # Change to your backend server URL
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set in environment")
# API_KEY = "secret-key"


def gather_checks():
    return {
        "disk_encrypted": check_disk_encryption(),
        "os_up_to_date": check_os_updates(),
        "antivirus": check_antivirus(),
        "inactivity_sleep_minutes": check_sleep_setting(),
    }


def send_report():
    machine_id = get_machine_id()
    payload = {
        "machine_id": machine_id,
        "hostname": platform.node(),
        "os": {"name": platform.system(), "version": platform.version()},
        "checks": gather_checks(),
        "timestamp": datetime.now(timezone.utc).isoformat()
        # "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    last_report = load_last_report()
    if not has_changed(payload, last_report):
        logger.info("No changes detected, skipping send")
        # r = requests.post(
        #     "http://localhost:8000/api/v1/report", json=payload, headers={"X-API-Key": API_KEY}, timeout=10  # nedd to change this to your backend URL
        # )

        # print("No changes detected, skipping send")
        # print(payload)
        return
    try:
        r = requests.post(
           SERVER_URL , json=payload, headers={"X-API-Key": API_KEY}, timeout=10
        )
        logger.info(f"Sent report, status {r.status_code}")
        print(f"Sent report, status {r.status_code}")
        save_last_report(payload)
    except Exception as e:
        logger.error(f"Failed to send report: {e}")
        print(f"Failed to send report: {e}")


class BackgroundDaemon:
    def __init__(self, interval_minutes=30):
        self.interval = interval_minutes

    def start(self):
        logger.info(f"Starting background mode, interval={self.interval} min")
        while True:
            send_report()
            time.sleep(self.interval )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="System Utility Client")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "--background", action="store_true", help="Run continuously in background"
    )
    parser.add_argument(
        "--interval", type=int, default=30, help="Interval in minutes for background mode"
    )
    args = parser.parse_args()

    if args.once:
        send_report()

    elif args.background:
        daemon = BackgroundDaemon(interval_minutes=args.interval)
        daemon.start()

    else:
        parser.print_help()
