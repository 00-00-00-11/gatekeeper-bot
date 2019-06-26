from bot.utils import request_answer, Permission


def create_permset(db, role, name: str, permissions: list) -> (bool, str):
    """
    Create a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if db.exists(key):
        return False, "Permset entry already exists"

    db.sadd(key, *[perm.value for perm in permissions])
    return True, "Created permsets"


def edit_permset(db, role, name: str, permissions: list) -> bool:
    """
    Modify a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if not db.exists(key):
        return False, "Permset does not exist"

    db.delete(key)
    db.sadd(key, *[perm.value for perm in permissions])
    return True, "Permset configured"


def create_role(db, role, user):
    """
    Create a role entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}"

    if db.exists(key):
        return

    create_permset(db, role, "administrators", Permission.all())
    db.set(f"{key}:member:{user.id}", "administrators")


def check_for_perm(db, role, user, permission):
    """
    Check a user for a specific permission.
    """

    # get the user's permset for that role
    user_key = f"guild:{role.guild.id}:role:{role.id}:member:{user.id}"
    permset = db.get(user_key)

    # if the user does not have a permset for the specified role, return false
    if not permset:
        return False

    permset = permset.decode()

    # get all the permissions associated with that permset
    permset_key = f"guild:{role.guild.id}:role:{role.id}:permset:{permset}"
    permissions = [int(p.decode()) for p in db.smembers(permset_key)]

    # return whether or not the specified permission is in the permset
    return permission.value in permissions
