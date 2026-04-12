import logging
from datetime import timedelta
from io import BytesIO
import json

from minio import Minio
from minio.error import S3Error

from api.config import settings

logger = logging.getLogger(__name__)


def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def ensure_bucket_exists(bucket_name: str) -> None:
    client = get_minio_client()
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            client.set_bucket_policy(bucket_name, json.dumps(policy))
            logger.info(f"Created bucket: {bucket_name}")
    except S3Error as e:
        logger.error(f"Failed to create bucket {bucket_name}: {e}")
        raise


def save_file_to_minio(bucket_name: str, filename: str, content: bytes) -> str:
    ensure_bucket_exists(bucket_name)

    client = get_minio_client()
    try:
        client.put_object(
            bucket_name,
            filename,
            data=BytesIO(content),
            length=len(content),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        logger.info(f"Saved file {filename} to bucket {bucket_name}")
        return f"s3://{bucket_name}/{filename}"
    except S3Error as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise


def generate_presigned_url(bucket_name: str, filename: str, expires: int = 600) -> str:
    return f"http://{settings.minio_public_url}/{bucket_name}/{filename}"