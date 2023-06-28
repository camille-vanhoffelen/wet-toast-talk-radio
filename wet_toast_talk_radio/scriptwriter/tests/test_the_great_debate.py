import asyncio

import pytest
from guidance.llms import Mock

from wet_toast_talk_radio.media_store import MediaStore, VirtualMediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.the_great_debate import TheGreatDebate


def test_the_great_debate(fake_llm, virtual_media_store, show_id):
    show = TheGreatDebate.create(fake_llm, virtual_media_store)
    asyncio.run(show.awrite(show_id=show_id))
    script_shows = virtual_media_store.list_script_shows()
    assert script_shows == [show_id]


def test_broken_the_great_debate(broken_fake_llm, virtual_media_store, show_id):
    show = TheGreatDebate.create(broken_fake_llm, virtual_media_store)
    with pytest.raises(AssertionError):
        asyncio.run(show.awrite(show_id=show_id))


def test_topic_cycling(fake_llm, virtual_media_store):
    show1 = TheGreatDebate.create(fake_llm, virtual_media_store)
    show2 = TheGreatDebate.create(fake_llm, virtual_media_store)
    assert show1.topic != show2.topic


@pytest.fixture()
def topic() -> str:
    return "toilet paper"


@pytest.fixture()
def script(topic: str) -> str:
    return f"Alice: I love {topic}.\n\nBob: I hate {topic}.\n\nAlice: Let's agree to disagree."


@pytest.fixture()
def bad_script() -> str:
    return "This isn't a script at all!"


@pytest.fixture()
def show_id() -> ShowId:
    return ShowId(show_i=0, date="2021-01-01")


@pytest.fixture()
def fake_llm(topic: str, script: str) -> Mock:
    in_favor_guest = f"Meet Alice. Alice loves {topic}."
    against_guest = f"Meet Bob. Bob hates {topic}."
    return Mock(output=[in_favor_guest, against_guest, script])


@pytest.fixture()
def broken_fake_llm(topic: str, bad_script: str) -> Mock:
    in_favor_guest = f"Meet Alice. Alice loves {topic}."
    against_guest = f"Meet Bob. Bob hates {topic}."
    return Mock(output=[in_favor_guest, against_guest, bad_script])


@pytest.fixture()
def virtual_media_store() -> MediaStore:
    return VirtualMediaStore(load_test_data=False)
