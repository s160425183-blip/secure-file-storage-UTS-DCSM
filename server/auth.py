import jwt
from datetime import datetime, timedelta, timezone


SECRET_KEY = "maulana-secure-storage-jwt-secret-2026"
ALGORITHM = "HS256"


USERS = {
    "maulana": {
        "password": "maulana123",
        "role": "user"
    },
    "admin": {
        "password": "admin123",
        "role": "admin"
    }
}


def generate_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None
