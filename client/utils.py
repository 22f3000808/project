import os
import json
import uuid
import logging
from datetime import datetime

CONFIG_DIR = os.path.expanduser("~/.sysutil")
LAST_REPORT_FILE = os.path.join(CONFIG_DIR, "last_report.json")
MACHINE_ID_FILE = os.path.join(CONFIG_DIR, "machine_id")
LOG_DIR = os.path.join(CONFIG_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "client.log")

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# --- Logging setup ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("sysutil")


def get_machine_id():
    """Load or create a persistent UUID for this machine."""
    if os.path.exists(MACHINE_ID_FILE):
        with open(MACHINE_ID_FILE, "r") as f:
            return f.read().strip()
    mid = str(uuid.uuid4())
    with open(MACHINE_ID_FILE, "w") as f:
        f.write(mid)
    logger.info(f"Generated new machine ID: {mid}")
    return mid


def load_last_report():
    """Load the last report from disk."""
    if not os.path.exists(LAST_REPORT_FILE):
        return None
    try:
        with open(LAST_REPORT_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading last report: {e}")
        return None


def save_last_report(report):
    """Save the last report to disk."""
    try:
        with open(LAST_REPORT_FILE, "w") as f:
            json.dump(report, f)
        logger.info("Last report saved")
    except Exception as e:
        logger.error(f"Error saving last report: {e}")


def has_changed(new_report, old_report, max_age_minutes=60):
    """Return True if checks have changed or last report too old."""
    if not old_report:
        return True
    try:
        old_checks = old_report.get("checks", {})
        new_checks = new_report.get("checks", {})
        if old_checks != new_checks:
            logger.info("Detected change in checks")
            return True
        # Check timestamp age
        old_ts = datetime.fromisoformat(old_report["timestamp"].replace("Z", ""))
        age_minutes = (datetime.utcnow() - old_ts).total_seconds() / 60
        if age_minutes > max_age_minutes:
            logger.info("Last report too old, sending again")
            return True
    except Exception as e:
        logger.error(f"Error comparing reports: {e}")
        return True
    return False
