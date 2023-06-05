import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ShowType(Enum):
    RAW = "raw"
    TRANSCODED = "transcoded"


@dataclass
class VirtualObject:
    show_name: str
    data: bytes
    last_modified: datetime
    show_type: ShowType


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class VirtualBucket(metaclass=SingletonMeta):
    """VirtualBucket is a thread-safe in-memory singleton dictionary"""

    def __init__(self):
        self._data: dict[str, VirtualObject] = {}
        self._lock = threading.Lock()

    def __getitem__(self, key: str) -> VirtualObject:
        with self._lock:
            return self._data[key]

    def __setitem__(self, key: str, value: VirtualObject):
        with self._lock:
            self._data[key] = value

    def __delitem__(self, key: str):
        with self._lock:
            del self._data[key]

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def get(self, key: str, default=None | VirtualObject) -> VirtualObject | None:
        with self._lock:
            return self._data.get(key, default)

    def keys(self) -> list[str]:
        with self._lock:
            return list(self._data.keys())

    def values(self) -> list[VirtualObject]:
        with self._lock:
            return list(self._data.values())

    def items(self) -> list[tuple[str, VirtualObject]]:
        with self._lock:
            return list(self._data.items())

    def reset(self):
        with self._lock:
            self._data = {}
