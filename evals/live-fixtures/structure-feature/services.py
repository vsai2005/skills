from repository import update_settings


def normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def update_account_settings(user_id: str, display_name: str) -> dict:
    return update_settings(user_id, normalize_name(display_name))
