from domain import final_price


def quote_response(cents: int, discount_percent: int) -> dict:
    return {"final_cents": final_price(cents, discount_percent)}
