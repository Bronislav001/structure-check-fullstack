from __future__ import annotations

import time
import uuid


def now_ms() -> int:
    return int(time.time() * 1000)


def make_id(prefix: str) -> str:
    raw = uuid.uuid4().hex  # 32 hex
    return f"{prefix}_{raw[:10]}"
