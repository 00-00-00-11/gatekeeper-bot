import re

from redis import Redis

from bot.utils import Permission


class db_connection:
    def __enter__(self):
        db = Redis()
        return db

    def __exit__(self, type, value, traceback):
        pass


class CreationError(Exception):
    pass


class DataSet:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Permset(DataSet):
    """
    Object representing a permset database entry.
    """

    def __str__(self):
        return self.name

    @property
    def giveable(self):
        """
        Return a list of permissions that can be granted to new Permsets
        created by a member of this Permset.
        """

        permissions = self.permissions

        try:
            permissions.remove(Permission.MANAGE_USERS)
            permissions.remove(Permission.MANAGE_PERMSETS)
            return permissions
        except ValueError:
            return None

    @property
    def role(self):
        """
        Return a role this permset is related to.
        """

        match = re.search(r"([\w\d:]+):permset:", self.key_prefix)
        return Role.get_raw(match.group(1))

    @property
    def _member_keys(self) -> list:
        """
        Return all members of this permset.
        """

        match = re.search(r"([\w\d:]+):permset:", self.key_prefix)
        result = f"{match.group(1)}:member:*"

        with db_connection() as db:
            def check(result):
                return True if db.get(result).decode() == self.name else False

            results = filter(check, db.scan_iter(match=result))

        return [r.decode() for r in results]

    def add_member(
            self,
            user: object) -> None:
        """
        Add a user to this permset.
        """

        user_key = f"{self.role.key}:member:{user.id}"

        with db_connection() as db:
            db.set(user_key, self.name)

    def has_permission(self, permission: object) -> bool:
        """
        Check if a permset has a permission.
        """

        for my_permission in self.permissions:
            if my_permission().value == permission.value:
                return True
        return False

    @staticmethod
    def exists(
            name: str,
            role: object = None,
            key: str = None) -> bool:
        """
        Check if a permset exists.
        """

        if key:
            role_key = key
        elif role:
            role_key = Role.get(role).key
        else:
            raise RuntimeError
        key = f"{role_key}:permset:{name}"

        with db_connection() as db:
            return db.exists(key)

    @staticmethod
    def get(
            role: object,
            name: str) -> object or None:
        """
        Get a Permset object by role and name.
        """

        return Permset.get_raw(f"guild:{role.guild.id}:role:{role.id}:permset:{name}")

    @staticmethod
    def get_raw(
            key: str) -> list:
        """
        Get a Permset object by database key.
        """

        with db_connection() as db:
            permints = db.smembers(key)

        if permints:
            permissions = [Permission.from_value(p.decode()) for p in permints]
            match = re.search(r"(guild:\d+:role:\d+:permset:)(.+$)", key)
            key_prefix = match.group(1)
            name = match.group(2)
            return Permset(
                name=name,
                key_prefix=key_prefix,
                permissions=permissions)
        return None

    @staticmethod
    def get_all(
            role: object) -> list:
        """
        Get all Permsets for a role.
        """

        role_key = Role.get(role).key
        match = f"{role_key}:permset:*"

        with db_connection() as db:
            results = db.scan_iter(match=match)

        return [Permset.get_raw(key.decode()) for key in results]

    @staticmethod
    def for_user(
            role,
            user):
        """
        Get the Permset object for a user.
        """

        key_prefix = f"guild:{role.guild.id}:role:{role.id}:"

        with db_connection() as db:
            name = db.get(
                f"{key_prefix}member:{user.id}")

        return Permset.get_raw(f"{key_prefix}permset:{name.decode()}")

    @staticmethod
    def create(
            role: object,
            name: str,
            permissions: list) -> object:
        """
        Create an entry for a permission set in the database.
        Return an object representing that entry.
        """

        permints = [perm().value for perm in permissions]
        key_prefix = f"guild:{role.guild.id}:role:{role.id}:permset:"
        key = f"{key_prefix}{name}"

        with db_connection() as db:
            if db.exists(key):
                raise CreationError(
                    "Permission set entry already exists.")
            db.sadd(key, *permints)

        return Permset(
            name=name,
            key_prefix=key_prefix,
            permissions=permissions)

    def update(
            self,
            name: str = None,
            permissions: list = None):
        """
        Update a Permset in place, as well as its database entry.
        """

        if name:
            with db_connection() as db:
                permints = db.smembers(f"{self.key_prefix}{self.name}")
                db.sadd(f"{self.key_prefix}{name}", *permints)
                db.delete(f"{self.key_prefix}{self.name}")
            self.name = name

        if permissions:
            permints = [perm().value for perm in permissions]
            with db_connection() as db:
                db.delete(f"{self.key_prefix}{self.name}")
                db.sadd(f"{self.key_prefix}{self.name}", *permints)
            self.permissions = permissions

    def delete(
            self):
        """
        Delete a Permset and its database entry.
        """

        with db_connection() as db:
            db.delete(f"{self.key_prefix}{self.name}", *self._member_keys)


class Role(DataSet):
    """
    Object representing a role database entry.
    """

    @property
    def members(self) -> list:
        """
        All members in this role.
        """

        match = f"{self.key}:member:*"

        with db_connection() as db:
            results = db.scan_iter(match=match)

        members = []
        for result in results:
            match = re.search(r"[\w\d:]+:member:(.+$)", result.decode())
            user_id = int(match.group(1))
            members.append(user_id)

        return members

    @property
    def permsets(self) -> list:
        """
        All permsets for this role.
        """

        with db_connection() as db:
            results = db.scan_iter(match=f"{self.key}:permset:*")

        return [Permset.get_raw(r.decode()) for r in results]

    def add_member(
            self,
            user: object,
            permset: str) -> None:
        """
        Add a user to this role under a permset by its name.
        """

        if Permset.exists(permset, key=self.key):
            user_key = f"{self.key}:member:{user.id}"

            with db_connection() as db:
                if db.exists(user_key):
                    raise CreationError()
                db.set(user_key, permset)

    def update_member(
            self,
            user: object,
            permset: str) -> None:
        """
        Change a members permset.
        """

        if Permset.exists(permset, key=self.key):
            user_key = f"{self.key}:member:{user.id}"

            with db_connection() as db:
                if db.exists(user_key):
                    db.set(user_key, permset)

    def check_member_for_perm(
            self,
            user: object,
            permission: object) -> bool:
        """
        Check a user for a specific permission.
        """

        user_key = f"{self.key}:member:{user.id}"

        with db_connection() as db:
            permset_name = db.get(user_key).decode()
        permset = Permset.get_raw(f"{self.key}:permset:{permset_name}")

        return permset.has_permission(permission)

    def remove_member(
            self,
            user: object) -> None:
        """
        Remove a member from a role.
        """

        user_key = f"{self.key}:member:{user.id}"

        with db_connection() as db:
            db.delete(user_key)

    @staticmethod
    def get_raw(
            key: str) -> object:
        """
        Get a Role object by key.
        """

        with db_connection() as db:
            if not [r for r in db.scan_iter(match=f"{key}:*")]:
                return None

        return Role(
            key=key)

    @staticmethod
    def get(
            role: object) -> object:
        """
        Get a Role object for Discord role.
        """

        return Role.get_raw(f"guild:{role.guild.id}:role:{role.id}")

    @staticmethod
    def create(
            role,
            user) -> object:
        """
        Create an entry for a permission set in the database.
        Return an object representing that entry.
        """

        key = f"guild:{role.guild.id}:role:{role.id}"
        user_key = f"{key}:member:{user.id}"

        with db_connection() as db:
            if db.exists(key):
                raise CreationError(
                    "Role already exists.")

            admin = Permset.create(
                role,
                "administrators",
                Permission.all())

            Permset.create(
                role,
                "default",
                Permission.default())

            db.set(user_key, admin.name)

        return Role(
            key=key)

    def delete(
            self) -> None:
        """
        Delete a role and its data.
        """

        for permset in self.permsets:
            permset.delete()

        with db_connection() as db:
            for member in self.members:
                key = f"{self.key}:member:{member}"
                db.delete(key)

            db.delete(self.key)
