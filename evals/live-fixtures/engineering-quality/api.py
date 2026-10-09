from storage import read_name


def profile(record: dict) -> dict:
    return {"display_name": read_name(record)}
