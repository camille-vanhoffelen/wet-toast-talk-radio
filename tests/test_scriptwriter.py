import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    media_store,  # noqa: F401
)
from wet_toast_talk_radio.scriptwriter import Scriptwriter
from wet_toast_talk_radio.scriptwriter.config import LLMConfig, ScriptwriterConfig


class TestScriptwriter:
    @pytest.mark.integration()
    def test_scriptwriter(
        self,
        _clear_bucket,  # noqa: PT019, F811
        media_store,  # noqa: F811
        llm_config,
    ):
        cfg = ScriptwriterConfig(llm=llm_config)
        scriptwriter = Scriptwriter(cfg=cfg, media_store=media_store)
        topic = "toilet paper"
        scriptwriter.run(topic)
        # TODO how will scriptwriter be triggered?
        assert len(media_store.list_script_shows()) == 1


@pytest.fixture()
def llm_config() -> LLMConfig:
    in_favor_guest = "Meet Alice. Alice loves toilet paper."
    against_guest = "Meet Bob. Bob hates toilet paper."
    script = "Alice: I love toilet paper.\n\nBob: I hate toilet paper.\n\nAlice: Let's agree to disagree."
    return LLMConfig(
        virtual=True, fake_responses=[in_favor_guest, against_guest, script]
    )
