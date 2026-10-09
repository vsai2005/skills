def status_for_role(role: str) -> int:
    # BUG: every known user is allowed into the admin-only operation.
    return 200 if role in {"admin", "viewer"} else 401
