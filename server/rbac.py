ROLE_PERMISSIONS = {
    "user": {
        "PUBLIC": True,
        "SECRET": False
    },
    "admin": {
        "PUBLIC": True,
        "SECRET": True
    }
}


def has_permission(role, security_label):
    permissions = ROLE_PERMISSIONS.get(role)

    if permissions is None:
        return False

    return permissions.get(security_label, False)
