import os
from datetime import datetime, timezone


LOG_FILE = "logs/audit.log"


def write_audit_log(username, role, action, filename, security_label, result):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now(timezone.utc).astimezone().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    log_entry = (
        f"[{timestamp}] "
        f"user={username} "
        f"role={role} "
        f"action={action} "
        f"file={filename} "
        f"label={security_label} "
        f"result={result}\n"
    )

    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
