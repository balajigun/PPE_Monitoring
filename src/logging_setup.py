import sys
import os
from datetime import datetime


class Tee:
    def __init__(self, terminal, logfile):
        self.terminal = terminal
        self.logfile = logfile

    def write(self, message):
        self.terminal.write(message)
        self.logfile.write(message)
        self.logfile.flush()

    def flush(self):
        self.terminal.flush()
        self.logfile.flush()


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = os.path.join(
        log_dir,
        f"logfile_{timestamp}.txt"
    )

    logfile = open(
        log_file,
        "w",
        encoding="utf-8"
    )

    sys.stdout = Tee(sys.__stdout__, logfile)
    sys.stderr = Tee(sys.__stderr__, logfile)

    print("=" * 70)
    print("PPE MONITORING APPLICATION")
    print("=" * 70)
    print(f"Application started : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log file            : {log_file}")
    print("=" * 70)

    return logfile