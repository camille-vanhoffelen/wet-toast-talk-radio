import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,
    message_queue,
    radio_operator,  # noqa: F401
    setup_bucket,  # noqa: F401
)
from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestAudioGenerator:
    @pytest.mark.integration()
    def test_audio_generator(
        self, _clear_bucket, _clear_sqs, media_store, message_queue  # noqa: PT019, F811
    ):
        today = "2012-12-21"
        show0 = ShowId(59, today)
        show1 = ShowId(60, today)
        shows = [show0, show1]
        media_store.put_script_show(show0, "John: Toast is wet!")
        media_store.put_script_show(show1, "Anna: No, it's not.")
        message_queue.add_stream_shows(shows)

        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(
            cfg=cfg, media_store=media_store, message_queue=message_queue
        )
        audio_generator.run()

        for s in shows:
            assert s in media_store.list_raw_shows()

    @pytest.mark.integration()
    def test_empty_queue(
        self,
        media_store,
        message_queue,
    ):
        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(
            cfg=cfg, media_store=media_store, message_queue=message_queue
        )
        # TODO should exit
        audio_generator.run()

        assert not media_store.list_raw_shows()
