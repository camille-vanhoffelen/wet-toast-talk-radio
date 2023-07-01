from pathlib import Path

from pydantic import BaseModel


class Speaker(BaseModel):
    """A speaker in a dialogue"""

    name: str
    gender: str


class Line(BaseModel):
    """A statement made by a speaker as part of a dialogue.
    e.g: Don't forget your lines!"""

    content: str
    speaker: Speaker


def read_lines(path: Path) -> list[Line]:
    with path.open("r") as file:
        return [Line.parse_raw(line) for line in file]
