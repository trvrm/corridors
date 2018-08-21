import uuid


class User:
    """
        Human player.
    """

    def __init__(self, name):
        self.uuid = uuid.uuid4()
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"User ({self.name}:{self.uuid})"

    def __json__(self):
        return {"name": self.name, "uuid": self.uuid}
