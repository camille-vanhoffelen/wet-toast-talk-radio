import json
import os
from typing import Generic, TypeVar

import boto3
import structlog
from botocore.exceptions import ClientError
from pydantic import (
    ValidationError,
)
from pydantic.fields import ModelField

from wet_toast_talk_radio.common.aws_clients import AWS_REGION

logger = structlog.get_logger()

secrets_manager_client = boto3.client("secretsmanager", region_name=AWS_REGION)

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
        if not field.sub_fields:
            raise TypeError("No generic type provided")

        generic_type_field = field.sub_fields[0]
        valid_value, error = generic_type_field.validate(v, {}, loc="val")
        if error:
            raise ValidationError(error, cls)

        return cls(valid_value, field_name=field.name)
