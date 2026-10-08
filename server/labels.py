SECRET_FILES = {
    "secret.txt",
    "confidential.txt"
}


def get_security_label(filename):
    if filename in SECRET_FILES:
        return "SECRET"

    return "PUBLIC"
