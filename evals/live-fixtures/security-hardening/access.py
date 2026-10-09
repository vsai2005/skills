def can_update_project(actor_id: str, actor_role: str, current_owner_id: str, requested_owner_id: str) -> bool:
    # BUG: authorization is checked against attacker-controlled future state.
    return actor_role == "admin" or actor_id == requested_owner_id


def update_project_owner(actor_id: str, actor_role: str, current_owner_id: str, requested_owner_id: str) -> str:
    if not can_update_project(actor_id, actor_role, current_owner_id, requested_owner_id):
        raise PermissionError("forbidden")
    return requested_owner_id
