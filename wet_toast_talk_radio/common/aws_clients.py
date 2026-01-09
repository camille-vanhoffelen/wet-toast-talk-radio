import os

import boto3

LOCAL_ENDPOINT = "http://localhost:4566"

session = boto3.Session()

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

sqs_client = session.client("sqs", region_name=AWS_REGION)
sqs_client_local = session.client(
    "sqs", endpoint_url=LOCAL_ENDPOINT, region_name=AWS_REGION
)

s3_client = session.client("s3", region_name=AWS_REGION)
s3_client_local = session.client(
    "s3", endpoint_url=LOCAL_ENDPOINT, region_name=AWS_REGION
)


def new_sqs_client(local: bool = False):  # noqa: FBT001, FBT002
    if local:
        return sqs_client_local
    return sqs_client


def new_s3_client(local: bool = False):  # noqa: FBT001, FBT002
    if local:
        return s3_client_local
    return s3_client
