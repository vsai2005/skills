def final_price(cents: int, discount_percent: int) -> int:
    if not 0 <= discount_percent <= 100:
        raise ValueError("invalid discount")
    return cents * (100 - discount_percent) // 100
