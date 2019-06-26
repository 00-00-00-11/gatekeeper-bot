from bot.utils import Permission


def get_permset(db, role, name: str) -> list or None:
    """
    Get all the permissions for a permission set.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    permints = db.smembers(key)

    if permints:
        permissions = [Permission.from_value(p.decode()) for p in permints]
        return permissions
    return None


def get_giveable_permset(db, role, user) -> list:
    """
    Get a list of giveable permissions for a user.
    """

    user_key = f"guild:{role.guild.id}:role:{role.id}:member:{user.id}"
    permset = db.get(user_key)

    if not permset:
        return False

    permissions = get_permset(db, role, permset.decode())

    if Permission.CREATE_PERMSETS in permissions:
        permissions.pop(permissions.index(Permission.CREATE_PERMSETS))

    return permissions


def create_permset(db, role, name: str, permissions: list) -> (bool, str):
    """
    Create a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if db.exists(key):
        return False, "Permset entry already exists"

    db.sadd(key, *[perm().value for perm in permissions])
    return True, "Created permsets"


def edit_permset(db, role, name: str, permissions: list) -> (bool, str):
    """
    Modify a permission set entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"

    if not db.exists(key):
        return False, "Permset does not exist"

    db.delete(key)
    db.sadd(key, *[perm().value for perm in permissions])
    return True, "Permset configured"


def delete_permset(db, role, name: str):
    """
    Delete a permission set entry from the database.
    """

    delete_all_members_under(db, role, name)
    key = f"guild:{role.guild.id}:role:{role.id}:permset:{name}"
    db.delete(key)


def delete_all_permsets(db, role):
    """
    Delete all permsets related to a role.
    """

    pattern = f"guild:{role.guild.id}:role:{role.id}:permset:*"

    results = db.scan_iter(match=pattern)

    for result in results:
        db.delete(result)


def create_role(db, role, user):
    """
    Create a role entry in the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}"

    if db.exists(key):
        return

    create_permset(db, role, "administrators", Permission.all())
    db.set(f"{key}:member:{user.id}", "administrators")


def create_member(db, role, user, permset):
    """
    Create a member entry for a permset.
    """

    permset_key = f"guild:{role.guild.id}:role:{role.id}:permset:{permset}"
    if db.exists(permset_key):
        key = f"guild:{role.guild.id}:role:{role.id}:member:{user.id}"
        db.set(key, permset)


def delete_member(db, role, user):
    """
    Delete a member entry from the database.
    """

    key = f"guild:{role.guild.id}:role:{role.id}:member:{user.id}"
    db.delete(key)


def delete_all_members(db, role):
    """
    Delete all members of a role.
    """

    pattern = f"guild:{role.guild.id}:role:{role.id}:member:*"

    results = db.scan_iter(match=pattern)

    for result in results:
        db.delete(result)


def delete_all_members_under(db, role, permset):
    """
    Delete all members of a permset
    """

    pattern = f"guild:{role.guild.id}:role:{role.id}:member:*"

    results = db.scan_iter(match=pattern)

    for result in results:
        if db.get(result).decode() == permset:
            db.delete(result)


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
    return db.sismember(permset_key, permission().value)
