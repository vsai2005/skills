import re

IGNORED = {"the", "and", "please", "go", "c", "r"}
TECHNOLOGIES = {"go", "c", "c++", "r", "rust", "java", "javascript", "react"}
ALLOWED = {"javascript", "react"}


def tokens(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[A-Za-z+]+", text)]


def has_foreign_topic(text: str) -> bool:
    # BUG: recognized short technology names disappear before classification.
    meaningful = [token for token in tokens(text) if token not in IGNORED]
    return any(token in TECHNOLOGIES and token not in ALLOWED for token in meaningful)
