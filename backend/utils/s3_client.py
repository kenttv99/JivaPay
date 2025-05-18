import logging
import os
from typing import IO, Optional

import boto3
import aioboto3
from botocore.exceptions import BotoCoreError, ClientError

from backend.config.settings import settings

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# Clients (sync & async)
# ------------------------------------------------------------

_SYNC_CLIENT: Optional[boto3.client] = None


def _get_sync_client():
    global _SYNC_CLIENT
    if _SYNC_CLIENT is None:
        _SYNC_CLIENT = boto3.client(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            endpoint_url=settings.S3_ENDPOINT_URL,
            region_name="us-east-1",
        )
    return _SYNC_CLIENT


def upload_fileobj(file_obj: IO, bucket: str, key: str, content_type: str = "application/octet-stream") -> str:
    """Загружает объект в S3 синхронно (для Celery-/CLI-кода).

    Возвращает полный URL (endpoint/bucket/key). Бросает исключение ClientError при ошибке.
    """
    client = _get_sync_client()
    try:
        client.upload_fileobj(
            Fileobj=file_obj,
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type},
        )
        url = f"{settings.S3_ENDPOINT_URL}/{bucket}/{key}"
        logger.info("Uploaded object to S3: %s", url)
        return url
    except (BotoCoreError, ClientError) as e:
        logger.error("Failed to upload object to S3: %s", e, exc_info=True)
        raise


# ------------------------------------------------------------
# Async upload (FastAPI endpoints)
# ------------------------------------------------------------


async def upload_fileobj_async(file_obj: IO, bucket: str, key: str, content_type: str = "application/octet-stream") -> str:
    """Асинхронная загрузка объекта (использует aioboto3)."""

    session = aioboto3.Session()
    async with session.client(
        "s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
        region_name="us-east-1",
    ) as s3:
        try:
            await s3.put_object(Bucket=bucket, Key=key, Body=file_obj, ContentType=content_type)
            url = f"{settings.S3_ENDPOINT_URL}/{bucket}/{key}"
            logger.info("Uploaded object to S3 (async): %s", url)
            return url
        except (BotoCoreError, ClientError) as e:
            logger.error("Async S3 upload failed: %s", e, exc_info=True)
            raise


# Backwards compatibility alias
upload_file_sync = upload_fileobj 