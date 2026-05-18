from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def app_env(tmp_path, monkeypatch):
    monkeypatch.setenv("OBJECT_STORAGE_PROVIDER", "local")
    monkeypatch.setenv("JWT_SECRET", "test_jwt_secret_32_chars_long_1234")
    monkeypatch.setenv("SIGNED_URL_SECRET", "test_signed_secret_32_chars_long_5678")
    monkeypatch.setenv("PUBLIC_FRONTEND_URL", "http://localhost:5173")

    from app import db as db_module
    from app.services import object_store as store_module

    storage_dir = tmp_path / "storage"
    db_module.STORAGE_DIR = storage_dir
    db_module.DB_PATH = storage_dir / "app.db"

    store_module.OBJECTS_DIR = storage_dir / "objects"
    store_module.OBJECT_STORAGE_PROVIDER = "local"
    store_module.SIGNED_URL_SECRET = "test_signed_secret_32_chars_long_5678"

    from app.main import create_app

    app = create_app()
    return app


@pytest.fixture()
def client(app_env):
    with TestClient(app_env) as client:
        yield client

