import pytest
import structlog

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    media_store,  # noqa: F401
)
from wet_toast_talk_radio.scriptwriter import DailyProgram, Scriptwriter
from wet_toast_talk_radio.scriptwriter.config import LLMConfig, ScriptwriterConfig

logger = structlog.get_logger()


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
        scriptwriter.run()
        n_shows = len(DailyProgram.program)
        assert len(media_store.list_script_shows()) == n_shows


@pytest.fixture()
def llm_config() -> LLMConfig:
    in_favor_guest = "Meet Alice. Alice loves toilet paper."
    against_guest = "Meet Bob. Bob hates toilet paper."
    script = "Alice: I love toilet paper.\n\nBob: I hate toilet paper.\n\nAlice: Let's agree to disagree."
    fake_responses = [in_favor_guest, against_guest, script]
    n_shows = len(DailyProgram.program)
    logger.debug("Initialising FakeLLM", n_shows=n_shows)
    fake_responses = fake_responses * n_shows
    return LLMConfig(virtual=True, fake_responses=fake_responses)
