import hashlib


def calculate_sha256(data):
    """
    Menghitung SHA-256 dari data dalam bentuk bytes.
    """
    return hashlib.sha256(data).hexdigest()
