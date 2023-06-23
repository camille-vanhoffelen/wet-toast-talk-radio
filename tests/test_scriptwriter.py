import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
)
from wet_toast_talk_radio.scriptwriter import Scriptwriter
from wet_toast_talk_radio.scriptwriter.config import ScriptwriterConfig


class TestScriptwriter:
    @pytest.mark.integration()
    def test_scriptwriter(
        self,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
    ):
        cfg = ScriptwriterConfig(openai_api_key="fake_key")
        scriptwriter = Scriptwriter(cfg=cfg, media_store=media_store)
        topic = "toilet paper"
        scriptwriter.run(topic)
