def read_name(record: dict) -> str:
    # Existing records store a plain string under name.
    return str(record["name"])
