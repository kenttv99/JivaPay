import logging
from typing import IO
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# Initialize S3 client
_s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL
)


def upload_fileobj(file_obj: IO, bucket: str, key: str) -> str:
    """
    Uploads a file-like object to S3 and returns its URL.

    Args:
        file_obj: File-like object opened in binary mode.
        bucket: Name of the target S3 bucket.
        key: Object key (path/name) in the bucket.

    Returns:
        The full URL to the uploaded object.

    Raises:
        ClientError: If upload fails.
    """
    try:
        _s3_client.upload_fileobj(file_obj, Bucket=bucket, Key=key)
        url = f"{settings.S3_ENDPOINT_URL}/{bucket}/{key}"
        logger.info(f"Uploaded object to S3: {url}")
        return url
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload object to S3: {e}", exc_info=True)
        raise 