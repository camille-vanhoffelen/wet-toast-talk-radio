from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ShowType(Enum):
    RAW = "raw"
    TRANSCODED = "transcoded"
    SCRIPT = "script"


@dataclass
class VirtualObject:
    show_id: str
    data: bytes
    last_modified: datetime
    show_type: ShowType


class VirtualBucket:
    """VirtualBucket is a singleton virtual bucket as a dict"""

    def __init__(self):
        self._data: dict[str, VirtualObject] = {}

    def __getitem__(self, key: str) -> VirtualObject:
        return self._data[key]

    def __setitem__(self, key: str, value: VirtualObject):
        self._data[key] = value

    def __delitem__(self, key: str):
        del self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default=None | VirtualObject) -> VirtualObject | None:
        return self._data.get(key, default)

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def values(self) -> list[VirtualObject]:
        return list(self._data.values())

    def items(self) -> list[tuple[str, VirtualObject]]:
        return list(self._data.items())

    def reset(self):
        self._data = {}
