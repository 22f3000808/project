import time
import signal
import sys
from utils import logger
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY not set in environment")

class Daemon:
    def __init__(self, interval_minutes=1):
        self.interval = interval_minutes * 60  # seconds
        self.running = True

    def start(self):
        logger.info(f"Daemon started with interval {self.interval/60} minutes.")
        self._register_signals()
        try:
            from main import send_report
            while self.running:
                logger.info("Daemon cycle: sending report...")
                send_report()
                logger.info(f"Sleeping for {self.interval/60} minutes...")
                time.sleep(self.interval)
        except Exception as e:
            logger.error(f"Daemon encountered error: {e}")
            sys.exit(1)

    def stop(self, *args):
        logger.info("Daemon stopping...")
        self.running = False
        sys.exit(0)

    def _register_signals(self):
        try:
            signal.signal(signal.SIGINT, self.stop)
            signal.signal(signal.SIGTERM, self.stop)
        except Exception as e:
            logger.warning(f"Signal handling not fully supported: {e}")

if __name__ == "__main__":
    # Allow running daemon directly for testing
    interval = 1  # minutes
    d = Daemon(interval_minutes=interval)
    d.start()
