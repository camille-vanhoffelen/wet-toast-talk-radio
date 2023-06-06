import boto3

LOCAL_ENDPOINT = "http://localhost:4566"

session = boto3.Session()

sqs_client = session.client("sqs")
sqs_client_local = session.client("sqs", endpoint_url=LOCAL_ENDPOINT)

s3_client = session.client("s3")
s3_client_local = session.client("s3", endpoint_url=LOCAL_ENDPOINT)


def new_sqs_client(local: bool = False):  # noqa: FBT001, FBT002
    if local:
        return sqs_client_local
    return sqs_client


def new_s3_client(local: bool = False):  # noqa: FBT001, FBT002
    if local:
        return s3_client_local
    return s3_client
