_STORE = {"u1": {"display_name": "Old"}}


def update_settings(user_id: str, display_name: str) -> dict:
    _STORE[user_id] = {"display_name": display_name}
    return dict(_STORE[user_id])
