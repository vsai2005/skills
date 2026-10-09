def generate_report(rows: list[dict[str, object]]) -> str:
    cleaned = []
    for row in rows:
        name = str(row.get("name", "")).strip()
        if not name:
            raise ValueError("name required")
        score = int(row.get("score", 0))
        if score < 0:
            raise ValueError("score must be non-negative")
        cleaned.append((name, score))
    cleaned.sort(key=lambda item: (-item[1], item[0].lower()))
    lines = ["NAME | SCORE", "------------"]
    for name, score in cleaned:
        lines.append(f"{name} | {score}")
    total = sum(score for _, score in cleaned)
    lines.append("------------")
    lines.append(f"TOTAL | {total}")
    return "\n".join(lines)


def validate_rows(rows: list[dict[str, object]]) -> None:
    # Duplicates generate_report validation and is intentionally tangled.
    for row in rows:
        if not str(row.get("name", "")).strip():
            raise ValueError("name required")
        if int(row.get("score", 0)) < 0:
            raise ValueError("score must be non-negative")


def format_row(name: str, score: int) -> str:
    # Duplicates generate_report formatting.
    return f"{name.strip()} | {int(score)}"
