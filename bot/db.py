from bot.utils import request_answer, Permission


def create_group(db, role, name: str, permissions: list):
    """
    Create a permissions group entry in the database.
    """

    key = f"guild:{role.guild}:role:{role.id}:group:{name}"

    if db.exists(key):
        return

    db.sadd(key, *[perm.value for perm in permissions])


def create_role(db, role, user, parent_role=None):
    """
    Create a role entry in the database.
    """

    key = f"guild:{role.guild}:role:{role.id}"

    if db.exists(key):
        return

    if parent_role:
        db.set(key, parent_role)

    db.sadd(f"{key}:member:{user.id}", *Permission.all())
