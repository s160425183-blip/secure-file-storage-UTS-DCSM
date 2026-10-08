import json
import os


CHECKSUM_FILE = "logs/checksums.json"


def load_checksums():
    if not os.path.exists(CHECKSUM_FILE):
        return {}

    with open(CHECKSUM_FILE, "r") as f:
        return json.load(f)


def save_checksum(filename, checksum):
    os.makedirs("logs", exist_ok=True)

    checksums = load_checksums()

    checksums[filename] = checksum

    with open(CHECKSUM_FILE, "w") as f:
        json.dump(checksums, f, indent=4)


def get_checksum(filename):
    checksums = load_checksums()
    return checksums.get(filename)
