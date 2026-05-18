from __future__ import annotations

import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from datetime import timedelta
from io import BytesIO
from pathlib import Path
from typing import Literal

from minio import Minio
from minio.error import S3Error

from ..db import STORAGE_DIR
from ..errors import ApiError


OBJECTS_DIR = STORAGE_DIR / 'objects'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {
    'text/plain',
    'text/markdown',
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}
SIGNED_URL_SECRET = os.getenv('SIGNED_URL_SECRET', 'signed_url_dev_secret_change_me')
SIGNED_URL_TTL_SECONDS = int(os.getenv('SIGNED_URL_TTL_SECONDS', '900'))
OBJECT_STORAGE_PROVIDER = os.getenv('OBJECT_STORAGE_PROVIDER', 'minio').strip().lower() or 'minio'
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', '127.0.0.1:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'struct-check-files')
MINIO_SECURE = os.getenv('MINIO_SECURE', 'false').strip().lower() == 'true'
MINIO_PRESIGN_TTL_SECONDS = int(os.getenv('MINIO_PRESIGN_TTL_SECONDS', '900'))


@dataclass
class StoredObject:
    storage_key: str
    size: int
    original_name: str
    content_type: str
    provider: Literal['local', 'minio']


_minio_client: Minio | None = None
_bucket_checked = False


def _ensure_local_dir() -> None:
    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _clean_name(name: str) -> str:
    n = ''.join(ch for ch in str(name or 'file') if ch.isalnum() or ch in {'-', '_', '.'})
    return n or 'file'


def _build_local_storage_name(object_id: str, original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    return f'{object_id}{ext}'


def _is_minio_enabled() -> bool:
    return OBJECT_STORAGE_PROVIDER == 'minio'


def _get_minio() -> Minio:
    global _minio_client
    if _minio_client is None:
        _minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
    return _minio_client


def _ensure_bucket() -> None:
    global _bucket_checked
    if not _is_minio_enabled() or _bucket_checked:
        return
    client = _get_minio()
    try:
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
    except S3Error as exc:
        raise ApiError(503, 'OBJECT_STORAGE_ERROR', 'object storage is unavailable') from exc
    _bucket_checked = True


def ensure_object_store() -> None:
    if _is_minio_enabled():
        _ensure_bucket()
    else:
        _ensure_local_dir()


def make_signed_token(attachment_id: str, *, expires_at: int) -> str:
    payload = f'{attachment_id}:{expires_at}'.encode('utf-8')
    sig = hmac.new(SIGNED_URL_SECRET.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    return f'{expires_at}.{sig}'


def verify_signed_token(attachment_id: str, token: str) -> None:
    try:
        expires_raw, sig = str(token or '').split('.', 1)
        expires_at = int(expires_raw)
    except Exception as exc:
        raise ApiError(403, 'BAD_SIGNED_URL', 'invalid signed url') from exc

    if expires_at < int(time.time()):
        raise ApiError(403, 'BAD_SIGNED_URL', 'signed url expired')

    expected = make_signed_token(attachment_id, expires_at=expires_at)
    if not hmac.compare_digest(expected, str(token or '')):
        raise ApiError(403, 'BAD_SIGNED_URL', 'invalid signed url')


def build_download_url(base_url: str, attachment_id: str) -> str:
    expires_at = int(time.time()) + SIGNED_URL_TTL_SECONDS
    token = make_signed_token(attachment_id, expires_at=expires_at)
    return f'{base_url}/api/files/{attachment_id}?token={token}'


def store_bytes(content: bytes, *, attachment_id: str, original_name: str, content_type: str) -> StoredObject:
    ensure_object_store()
    content_type = str(content_type or 'application/octet-stream')
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ApiError(400, 'VALIDATION_ERROR', 'unsupported file type')
    if len(content) > MAX_FILE_SIZE:
        raise ApiError(400, 'VALIDATION_ERROR', 'file is too large (max 5 MB)')

    clean_name = _clean_name(original_name or 'attachment')

    if _is_minio_enabled():
        object_key = f'checks/{attachment_id}/{clean_name}'
        client = _get_minio()
        try:
            client.put_object(
                MINIO_BUCKET,
                object_key,
                BytesIO(content),
                length=len(content),
                content_type=content_type,
            )
        except S3Error as exc:
            raise ApiError(503, 'OBJECT_STORAGE_ERROR', 'failed to upload file to object storage') from exc
        return StoredObject(
            storage_key=object_key,
            size=len(content),
            original_name=clean_name,
            content_type=content_type,
            provider='minio',
        )

    storage_name = _build_local_storage_name(attachment_id, clean_name)
    storage_path = OBJECTS_DIR / storage_name
    storage_path.write_bytes(content)
    return StoredObject(
        storage_key=str(storage_path),
        size=len(content),
        original_name=clean_name,
        content_type=content_type,
        provider='local',
    )


def delete_object(storage_key: str) -> None:
    if not storage_key:
        return
    if _is_minio_enabled():
        try:
            _ensure_bucket()
            _get_minio().remove_object(MINIO_BUCKET, storage_key)
        except S3Error:
            return
        return
    try:
        os.remove(storage_key)
    except OSError:
        return


def resolve_download_target(storage_key: str) -> dict:
    if _is_minio_enabled():
        try:
            _ensure_bucket()
            url = _get_minio().presigned_get_object(
                MINIO_BUCKET,
                storage_key,
                expires=timedelta(seconds=MINIO_PRESIGN_TTL_SECONDS),
            )
        except S3Error as exc:
            raise ApiError(503, 'OBJECT_STORAGE_ERROR', 'failed to generate signed object url') from exc
        return {'mode': 'redirect', 'url': url}
    return {'mode': 'local_file', 'path': storage_key}


def storage_status() -> dict:
    return {
        'provider': 'minio' if _is_minio_enabled() else 'local',
        'bucket': MINIO_BUCKET if _is_minio_enabled() else None,
        'endpoint': MINIO_ENDPOINT if _is_minio_enabled() else None,
        'secure': MINIO_SECURE if _is_minio_enabled() else None,
    }
