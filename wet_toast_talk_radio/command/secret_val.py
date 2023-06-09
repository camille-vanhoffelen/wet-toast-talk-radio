import json
from typing import Generic, TypeVar

import boto3
import structlog
from botocore.exceptions import ClientError
from pydantic import ValidationError
from pydantic.fields import ModelField

logger = structlog.get_logger()
secrets_manager_client = boto3.client("secretsmanager")

T = TypeVar("T")


def _get_secret_val(field_name: str | None, raw_val: str) -> T:
    secret_id = raw_val.removeprefix("sm:/")
    try:
        response = secrets_manager_client.get_secret_value(SecretId=secret_id)
    except ClientError as e:
        logger.error(f"Failed to get secret value for {field_name}: {e}")

    secret_str = response["SecretString"]
    if field_name is None:
        return secret_str
    return json.loads(secret_str)[field_name]


class SecretVar(Generic[T]):
    def __init__(self, val: T, field_name: str | None = None) -> None:
        if isinstance(val, str) and val.startswith("sm:/"):
            val = _get_secret_val(field_name, val)
        self._val = val

    def value(self):
        return self._val

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField):
        if not isinstance(v, cls):
            raise TypeError("Invalid value")
        if not field.sub_fields:
            return v

        val_f = field.sub_fields[0]
        valid_value, error = val_f.validate(v._val, {}, loc="val")  # noqa: SLF001
        if error:
            raise ValidationError(error, cls)

        v._val = valid_value  # noqa: SLF001
        return v
