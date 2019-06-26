from bot.utils import request_answer, Permission


def create_permset(db, role, name: str, permissions: list):
    """
    Create a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if db.exists(key):
        return

    db.sadd(key, *[str(perm.value).encode('utf-8') for perm in permissions])


def create_role(db, role, user):
    """
    Create a role entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}"

    if db.exists(key):
        return

    create_permset(db, role, "administrators", Permission.all())
    db.set(f"{key}:member:{user.id}", "administrators".encode('utf-8'))


def check_for_perm(db, role, user, permission):
    """
    Check a user for a specific permission.
    """

    # get the user's permset for that role
    user_key = f"guild:{role.guild.id}:role:{role.id}:member:{user.id}"
    permset = db.get(user_key).decode('utf-8')

    # if the user does not have a permset for the specified role, return false
    if permset == 'None':
        return False

    # get all the permissions associated with that permset
    permset_key = f"guild:{role.guild.id}:role:{role.id}:permset:{permset}"
    permissions = list(map(
        lambda p: int(p.decode('utf-8')),
        db.smembers(permset_key)))

    # return whether or not the specified permission is in the permset
    return permission.value in permissions
