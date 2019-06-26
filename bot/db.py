from bot.utils import request_answer, Permission


def create_permset(db, role, name: str, permissions: list):
    """
    Create a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if db.exists(key):
        return

    db.sadd(key, *[perm.value for perm in permissions])


def create_role(db, role, user):
    """
    Create a role entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}"

    if db.exists(key):
        return

    create_permset(db, role, "administrators", Permission.all())
    db.set(f"{key}:member:{user.id}", "administrators")
