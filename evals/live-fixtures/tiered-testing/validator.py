import re


def valid_slug(value: str) -> bool:
    # New requirement: hyphens are valid between alphanumeric segments.
    return bool(re.fullmatch(r"[a-z0-9]+", value))
