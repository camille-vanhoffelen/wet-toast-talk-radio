import pytest

from tests.conftests import (
    _clear_bucket,  # noqa: F401
    _clear_sqs,  # noqa: F401
    media_store,  # noqa: F401
    message_queue,  # noqa: F401
)
from wet_toast_talk_radio.audio_generator import AudioGenerator
from wet_toast_talk_radio.audio_generator.config import AudioGeneratorConfig
from wet_toast_talk_radio.media_store import MediaStore
from wet_toast_talk_radio.media_store.media_store import ShowId


class TestAudioGenerator:
    @pytest.mark.integration()
    def test_audio_generator(
        self,
        mocker,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
        message_queue,  # noqa: F811
    ):
        delete_spy = mocker.spy(message_queue, "delete_script_show")
        shows = _init_bucket(media_store)
        message_queue.add_script_shows(shows)

        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(
            cfg=cfg, media_store=media_store, message_queue=message_queue
        )
        audio_generator.run()

        for s in shows:
            assert s in media_store.list_raw_shows()
        assert delete_spy.call_count == len(shows)
        assert message_queue.poll_script_show() is None

    @pytest.mark.integration()
    def test_empty_queue(
        self, _clear_bucket, _clear_sqs, media_store, message_queue  # noqa: PT019, F811
    ):
        _init_bucket(media_store)
        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(
            cfg=cfg, media_store=media_store, message_queue=message_queue
        )
        audio_generator.run()

        assert not media_store.list_raw_shows()

    @pytest.mark.integration()
    def test_heartbeat(
        self,
        mocker,
        _clear_bucket,  # noqa: PT019, F811
        _clear_sqs,  # noqa: PT019, F811
        media_store,  # noqa: F811
        message_queue,  # noqa: F811
    ):
        heartbeat_spy = mocker.spy(message_queue, "change_message_visibility_timeout")
        today = "2012-12-21"
        show666 = ShowId(666, today)
        n_sentences = 3
        media_store.put_script_show(
            show666,
            "Hi there. " * n_sentences,
        )
        message_queue.add_script_shows([show666])

        cfg = AudioGeneratorConfig(use_s3_model_cache=False, use_small_models=True)
        audio_generator = AudioGenerator(
            cfg=cfg, media_store=media_store, message_queue=message_queue
        )
        audio_generator.run()

        assert show666 in media_store.list_raw_shows()
        assert heartbeat_spy.call_count == n_sentences


def _init_bucket(store: MediaStore) -> list[ShowId]:
    today = "2012-12-21"
    show59 = ShowId(59, today)
    show60 = ShowId(60, today)
    store.put_script_show(show59, "John: Toast is wet!")
    store.put_script_show(show60, "Anna: No, it's not.")
    return [show59, show60]
