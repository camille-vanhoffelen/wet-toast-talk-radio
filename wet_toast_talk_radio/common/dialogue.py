from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel


@dataclass(eq=True, frozen=True)
class Speaker:
    """A speaker in a dialogue"""

    name: str
    gender: str
    host: bool
    speaking_rate: float = 0.93


class Line(BaseModel):
    """A statement made by a speaker as part of a dialogue.
    e.g: Don't forget your lines!"""

    content: str
    speaker: Speaker


def read_lines(path: Path) -> list[Line]:
    """Read a script file (.jsonl) where each file line is a pydantic Line json."""
    with path.open("r") as file:
        return [Line.parse_raw(line) for line in file]
