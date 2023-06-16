import os

import pytest
from botocore.stub import Stubber
from pydantic import BaseModel, BaseSettings

from wet_toast_talk_radio.command.config import RootConfig
from wet_toast_talk_radio.common.secret_val import SecretVar, secrets_manager_client
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
                    disc_jockey=None,
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

        class SubConfig(BaseModel):
            secret: SecretVar[str]

        class TestConfig(BaseSettings):
            sub: SubConfig | None = None

            class Config:
                env_nested_delimiter = "__"

        assert TestConfig().sub is None

        os.environ["SUB__SECRET"] = "sm:/wet_toast_talk_radio/my_secret"
        assert TestConfig().sub.secret.value() == "foo"
