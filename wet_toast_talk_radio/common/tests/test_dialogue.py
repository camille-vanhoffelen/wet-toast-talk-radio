from pathlib import Path

import pytest

from wet_toast_talk_radio.common.dialogue import read_lines


def test_read_lines(script_path: Path):
    n_lines = 2
    lines = read_lines(script_path)
    assert len(lines) == n_lines
    john_line = lines[0]
    assert john_line.speaker.name == "John"
    assert john_line.speaker.gender == "male"
    assert john_line.speaker.host is False
    assert john_line.content == "Toast is wet!"
    anna_line = lines[1]
    assert anna_line.speaker.name == "Anna"
    assert anna_line.speaker.gender == "female"
    assert anna_line.speaker.host is False
    assert anna_line.content == "No, it's not."


@pytest.fixture()
def script_path() -> Path:
    return Path(__file__).parent / "show69.jsonl"
