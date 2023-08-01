from wet_toast_talk_radio.scriptwriter.the_great_debate.topics import load_topics


def test_topics():
    names = load_topics()
    assert len(names) > 1
