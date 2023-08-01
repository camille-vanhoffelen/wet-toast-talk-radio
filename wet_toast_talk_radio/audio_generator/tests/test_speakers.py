import pytest

from wet_toast_talk_radio.audio_generator.speakers import init_voices
from wet_toast_talk_radio.common.dialogue import Speaker


def test_init_voices(speakers, host):
    voices = init_voices(speakers)
    assert len(voices) == len(speakers)
    assert all(speaker.name in voices for speaker in speakers)
    conditioning_latents = voices[host.name]
    assert conditioning_latents[0].mean().item() == pytest.approx(-0.041467275470495224)


def test_bad_host(bad_host):
    with pytest.raises(ValueError, match="Host name"):
        init_voices({bad_host})


@pytest.fixture()
def speakers(host, guest1, guest2) -> set[Speaker]:
    return {host, guest1, guest2}


@pytest.fixture()
def host() -> Speaker:
    return Speaker(name="Orion", gender="male", host=True)


@pytest.fixture()
def guest1() -> Speaker:
    return Speaker(name="Sophie", gender="female", host=False)


@pytest.fixture()
def guest2() -> Speaker:
    return Speaker(name="George", gender="male", host=False)


@pytest.fixture()
def bad_host() -> Speaker:
    return Speaker(name="Trololol", gender="female", host=True)
