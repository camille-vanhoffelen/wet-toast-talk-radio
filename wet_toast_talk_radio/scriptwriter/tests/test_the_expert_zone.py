import asyncio

import pytest
from guidance.llms import Mock

from wet_toast_talk_radio.media_store import MediaStore, VirtualMediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId
from wet_toast_talk_radio.scriptwriter.the_expert_zone import TheExpertZone


def test_the_expert_zone(fake_llm, virtual_media_store, show_id):
    show = TheExpertZone(
        expertise="Dust dynamics",
        trait="boring",
        llm=fake_llm,
        media_store=virtual_media_store,
    )
    asyncio.run(show.awrite(show_id=show_id))
    script_shows = virtual_media_store.list_script_shows()
    assert script_shows == [show_id]


@pytest.fixture()
def show_id() -> ShowId:
    return ShowId(show_i=0, date="2021-01-01")


@pytest.fixture()
def fake_llm() -> Mock:
    show = "Welcome to The Expert Zone!"
    return Mock(output=[show])


@pytest.fixture()
def virtual_media_store() -> MediaStore:
    return VirtualMediaStore(load_test_data=False)
