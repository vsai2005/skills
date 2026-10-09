def normalize_name(value: str) -> str:
    return " ".join(part.capitalize() for part in value.strip().split())
