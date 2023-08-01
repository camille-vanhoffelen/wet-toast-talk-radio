from wet_toast_talk_radio.scriptwriter.names import load_names


def test_names():
    names = load_names()
    assert len(names) > 1
