from time import sleep
from unittest.mock import AsyncMock

import pytest
import structlog

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    message_queue,  # noqa: F401
)
from wet_toast_talk_radio.scriptwriter import Scriptwriter
from wet_toast_talk_radio.scriptwriter.adverts import Advert
from wet_toast_talk_radio.scriptwriter.config import LLMConfig, ScriptwriterConfig

logger = structlog.get_logger()


class TestScriptwriter:
    @pytest.mark.integration()
    def test_scriptwriter(
        self,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
        message_queue,  # noqa: F811
        llm_config,
        program,
    ):
        cfg = ScriptwriterConfig(llm=llm_config)
        scriptwriter = Scriptwriter(
            cfg=cfg,
            media_store=media_store,
            message_queue=message_queue,
            program=program,
        )
        scriptwriter.run()
        n_shows = len(program)
        assert len(media_store.list_script_shows()) == n_shows
        for _ in range(n_shows):
            _poll_and_delete(message_queue)

    @pytest.mark.integration()
    def test_scriptwriter_failure(  # noqa: PLR0913
        self,
        mocker,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
        message_queue,  # noqa: F811
        llm_config,
        program,
    ):
        mocker.patch(
            "wet_toast_talk_radio.scriptwriter.adverts.Advert.awrite",
            side_effect=AsyncMock(side_effect=Exception("Random bug")),
        )
        cfg = ScriptwriterConfig(llm=llm_config)
        scriptwriter = Scriptwriter(
            cfg=cfg,
            media_store=media_store,
            message_queue=message_queue,
            program=program,
        )
        scriptwriter.run()
        assert len(media_store.list_script_shows()) == 0
        assert message_queue.poll_script_show() is None

    @pytest.mark.integration()
    def test_scriptwriter_daily_purge(  # noqa: PLR0913
        self,
        mocker,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
        message_queue,  # noqa: F811
        llm_config,
        program,
    ):
        cfg = ScriptwriterConfig(llm=llm_config)
        scriptwriter = Scriptwriter(
            cfg=cfg,
            media_store=media_store,
            message_queue=message_queue,
            program=program,
        )
        # day 1
        scriptwriter.run()
        n_shows = len(program)
        assert len(media_store.list_script_shows()) == n_shows

        # day 2
        mocker.patch(
            "wet_toast_talk_radio.scriptwriter.scriptwriter.get_offset_iso_utc_date",
            return_value="2012-12-21",
        )
        scriptwriter2 = Scriptwriter(
            cfg=cfg,
            media_store=media_store,
            message_queue=message_queue,
            program=program,
        )
        scriptwriter2.run()
        assert len(media_store.list_script_shows()) == n_shows

        for _ in range(n_shows):
            _poll_and_delete(message_queue)


@pytest.fixture()
def llm_config(program) -> LLMConfig:
    # Easy to mock daily program
    product_name = "Fancy pants"
    product_description = "Fancy pants are the best pants."
    fake_responses = [product_name, product_description]
    n_shows = len(program)
    logger.debug("Initialising FakeLLM", n_shows=n_shows)
    fake_responses = fake_responses * n_shows
    return LLMConfig(virtual=True, fake_responses=fake_responses)


@pytest.fixture()
def program():
    return Advert, Advert, Advert


def _poll_and_delete(message_queue):  # noqa: F811
    result = message_queue.poll_script_show()
    assert result is not None
    message_queue.delete_script_show(result.receipt_handle)
    sleep(0.1)
