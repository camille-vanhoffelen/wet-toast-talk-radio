from enum import Enum
import time


class Role(Enum):
    GUEST = "guest"
    HOST = "host"


class History:
    def __init__(self):
        self.messages = []

    def append(self, role: Role, message: str):
        # TODO remove stupid
        time.sleep(0.2)
        self.messages.append({"role": role, "message": message})

    @property
    def guest_history(self):
        guest_history = []
        for m in self.messages:
            role = "assistant" if m["role"] == Role.GUEST else "user"
            guest_history.append({"role": role, "message": m["message"]})
        return guest_history

    @property
    def host_history(self):
        host_history = []
        for m in self.messages:
            role = "assistant" if m["role"] == Role.HOST else "user"
            host_history.append({"role": role, "message": m["message"]})
        return host_history
