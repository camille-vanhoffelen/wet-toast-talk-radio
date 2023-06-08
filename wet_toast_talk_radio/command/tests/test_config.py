import os
from typing import Any

import pytest
from botocore.stub import Stubber
from pydantic import BaseSettings

from wet_toast_talk_radio.command.config import RootConfig
from wet_toast_talk_radio.command.secret_val import SecretVar, secrets_manager_client
from wet_toast_talk_radio.disc_jockey.config import DiscJockeyConfig
from wet_toast_talk_radio.media_store.config import MediaStoreConfig


@pytest.fixture()
def secrets_manager_stub():
    with Stubber(secrets_manager_client) as stubber:
        yield stubber


class TestConfig:
    @pytest.mark.parametrize(
        ("env", "expected"),
        [
            (
                {},
                RootConfig(),
            ),
            (
                {"WT_MEDIA_STORE__VIRTUAL": "true"},
                RootConfig(
                    media_store=MediaStoreConfig(virtual=True),
                    disc_jockey=DiscJockeyConfig(),
                    audio_generator=None,
                ),
            ),
        ],
    )
    def test_env_config(self, env: dict, expected: RootConfig):
        for key, value in env.items():
            os.environ[key] = value

        assert RootConfig() == expected

    def test_secret_manager_config(self, secrets_manager_stub):
        secrets_manager_stub.add_response(
            "get_secret_value",
            {
                "Name": "wet_toast_talk_radio/my_secret",
                "SecretString": '{"secret":"foo"}',
            },
            {"SecretId": "wet_toast_talk_radio/my_secret"},
        )

        class TestConfig(BaseSettings):
            secret: SecretVar[str] | None = None

            class Config:
                @classmethod
                def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
                    if field_name == "secret":
                        return SecretVar[str](raw_val, field_name)
                    return cls.json_loads(raw_val)

        assert TestConfig().secret is None

        os.environ["SECRET"] = "sm:/wet_toast_talk_radio/my_secret"
        assert TestConfig().secret.value() == "foo"
