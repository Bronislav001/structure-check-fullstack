from __future__ import annotations

import json
import sqlite3
from typing import Any, Dict, List, Optional

from fastapi import Request, UploadFile

from ..errors import ApiError
from ..rbac import PERMS, has_permission
from ..util import make_id, now_ms
from .template import get_default_template
from .analyze import analyze_text_against_template
from .object_store import build_download_url, delete_object, resolve_download_target, store_bytes, verify_signed_token
from .file_text import extract_text_from_bytes


VALID_SORTS = {'createdAt', 'updatedAt', 'label'}
VALID_DIRS = {'asc', 'desc'}
VALID_STATUS = {'all', 'ok', 'issues'}


def _validate_create(label: Any, text: Any, notes: Any = '') -> tuple[str, str, str]:
    l = str(label or '').strip()
    t = str(text or '')
    n = str(notes or '')
    if not l or len(l) < 2:
        raise ApiError(400, 'VALIDATION_ERROR', 'label is required (min 2 chars)')
    if len(l) > 120:
        raise ApiError(400, 'VALIDATION_ERROR', 'label max length is 120 chars')
    if not t or len(t.strip()) < 10:
        raise ApiError(400, 'VALIDATION_ERROR', 'text is required (min 10 chars)')
    if len(n) > 4000:
        raise ApiError(400, 'VALIDATION_ERROR', 'notes max length is 4000 chars')
    return l, t, n


def _assert_exists(row: Optional[sqlite3.Row]) -> None:
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'check not found')


def _assert_can_read(user: Dict[str, Any], row: sqlite3.Row) -> None:
    _assert_exists(row)
    if row['userId'] != user['id'] and not has_permission(user.get('role'), PERMS.CHECKS_READ_ANY):
        raise ApiError(403, 'FORBIDDEN', 'no access to this resource')


def _assert_can_update(user: Dict[str, Any], row: sqlite3.Row) -> None:
    _assert_exists(row)
    if row['userId'] != user['id'] and not has_permission(user.get('role'), PERMS.CHECKS_UPDATE_ANY):
        raise ApiError(403, 'FORBIDDEN', 'no access to this resource')


def _assert_can_delete(user: Dict[str, Any], row: sqlite3.Row) -> None:
    _assert_exists(row)
    if row['userId'] == user['id']:
        return
    if not has_permission(user.get('role'), PERMS.CHECKS_DELETE_ANY):
        raise ApiError(403, 'FORBIDDEN', 'no access to this resource')


def _attachments_for_check(db: sqlite3.Connection, check_id: str, request: Request) -> List[Dict[str, Any]]:
    rows = db.execute(
        '''
        SELECT id, checkId, originalName, contentType, size, createdAt
        FROM attachments
        WHERE checkId = ?
        ORDER BY createdAt DESC
        ''',
        (check_id,),
    ).fetchall()
    base_url = str(request.base_url).rstrip('/')
    return [
        {
            'id': r['id'],
            'checkId': r['checkId'],
            'originalName': r['originalName'],
            'contentType': r['contentType'],
            'size': int(r['size']),
            'createdAt': int(r['createdAt']),
            'downloadUrl': build_download_url(base_url, r['id']),
        }
        for r in rows
    ]


def _to_dto(row: sqlite3.Row | Dict[str, Any], request: Request, *, include_text: bool = False) -> Dict[str, Any]:
    def get(k: str) -> Any:
        return row[k] if not isinstance(row, dict) else row.get(k)

    dto = {
        'id': get('id'),
        'userId': get('userId'),
        'authorName': get('authorName'),
        'authorEmail': get('authorEmail'),
        'label': get('label'),
        'notes': get('notes'),
        'createdAt': int(get('createdAt')),
        'updatedAt': int(get('updatedAt')),
        'inputLength': int(get('inputLength')),
        'ok': bool(int(get('ok'))),
        'template': json.loads(get('templateJson')),
        'found': json.loads(get('foundJson')),
        'missing': json.loads(get('missingJson')),
        'orderIssues': json.loads(get('orderIssuesJson')),
        'attachments': _attachments_for_check(request.state.db, get('id'), request),
    }
    if include_text:
        dto['text'] = get('text')
    return dto




def create_check_from_upload(
    db: sqlite3.Connection,
    request: Request,
    *,
    user_id: str,
    label: Any,
    notes: Any = '',
    file: UploadFile,
) -> Dict[str, Any]:
    attachment_id = make_id('att')
    original_name = str(file.filename or 'attachment')
    content_type = str(file.content_type or 'application/octet-stream')
    content = file.file.read()

    stored = None
    try:
        stored = store_bytes(content, attachment_id=attachment_id, original_name=original_name, content_type=content_type)
        extracted_text = extract_text_from_bytes(content, content_type=stored.content_type, original_name=stored.original_name)
        final_label = str(label or '').strip() or stored.original_name
        created = create_check(db, request, user_id=user_id, label=final_label, text=extracted_text, notes=notes)
        created_at = now_ms()
        db.execute(
            '''
            INSERT INTO attachments (id, checkId, userId, originalName, storageKey, contentType, size, createdAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (attachment_id, created['id'], user_id, stored.original_name, stored.storage_key, stored.content_type, stored.size, created_at),
        )
        db.commit()
        request.state.db = db
        row = db.execute(
            '''
            SELECT c.*, u.name AS authorName, u.email AS authorEmail
            FROM checks c
            JOIN users u ON u.id = c.userId
            WHERE c.id = ?
            ''',
            (created['id'],),
        ).fetchone()
        return _to_dto(row, request, include_text=True)
    except Exception:
        if stored:
            delete_object(stored.storage_key)
        raise


def create_check(db: sqlite3.Connection, request: Request, *, user_id: str, label: Any, text: Any, notes: Any = '') -> Dict[str, Any]:
    l, t, n = _validate_create(label, text, notes)
    template = get_default_template()
    analysis = analyze_text_against_template(t, template)
    created_at = now_ms()
    check = {
        'id': make_id('chk'),
        'userId': user_id,
        'authorName': None,
        'authorEmail': None,
        'label': l,
        'text': t,
        'notes': n,
        'createdAt': created_at,
        'updatedAt': created_at,
        'inputLength': len(t),
        'ok': 1 if analysis['ok'] else 0,
        'templateJson': json.dumps(analysis['template'], ensure_ascii=False),
        'foundJson': json.dumps(analysis['found'], ensure_ascii=False),
        'missingJson': json.dumps(analysis['missing'], ensure_ascii=False),
        'orderIssuesJson': json.dumps(analysis['orderIssues'], ensure_ascii=False),
    }

    db.execute(
        '''
        INSERT INTO checks (
          id, userId, label, text, notes, createdAt, updatedAt,
          inputLength, ok, templateJson, foundJson, missingJson, orderIssuesJson
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            check['id'], check['userId'], check['label'], check['text'], check['notes'],
            check['createdAt'], check['updatedAt'], check['inputLength'], check['ok'],
            check['templateJson'], check['foundJson'], check['missingJson'], check['orderIssuesJson'],
        ),
    )
    db.commit()

    row = db.execute(
        '''
        SELECT c.*, u.name AS authorName, u.email AS authorEmail
        FROM checks c
        JOIN users u ON u.id = c.userId
        WHERE c.id = ?
        ''',
        (check['id'],),
    ).fetchone()
    request.state.db = db
    return _to_dto(row, request, include_text=True)


def list_checks(
    db: sqlite3.Connection,
    request: Request,
    *,
    user: Dict[str, Any],
    scope: str | None = None,
    q: str = '',
    status: str = 'all',
    sort_by: str = 'createdAt',
    sort_dir: str = 'desc',
    page: int = 1,
    page_size: int = 5,
    owner_id: str | None = None,
) -> Dict[str, Any]:
    request.state.db = db
    scope = 'all' if scope == 'all' and has_permission(user.get('role'), PERMS.CHECKS_READ_ANY) else 'own'
    status = status if status in VALID_STATUS else 'all'
    sort_by = sort_by if sort_by in VALID_SORTS else 'createdAt'
    sort_dir = sort_dir if sort_dir in VALID_DIRS else 'desc'
    page = max(1, int(page or 1))
    page_size = min(20, max(1, int(page_size or 5)))
    q = str(q or '').strip()
    owner_id = str(owner_id or '').strip()

    where_parts = []
    params: List[Any] = []

    if scope != 'all':
        where_parts.append('c.userId = ?')
        params.append(user['id'])
    elif owner_id:
        where_parts.append('c.userId = ?')
        params.append(owner_id)

    if q:
        where_parts.append('(LOWER(c.label) LIKE ? OR LOWER(c.text) LIKE ? OR LOWER(c.notes) LIKE ? OR LOWER(u.name) LIKE ? OR LOWER(u.email) LIKE ?)')
        like = f'%{q.lower()}%'
        params.extend([like, like, like, like, like])

    if status == 'ok':
        where_parts.append('c.ok = 1')
    elif status == 'issues':
        where_parts.append('c.ok = 0')

    where_sql = f"WHERE {' AND '.join(where_parts)}" if where_parts else ''

    total_row = db.execute(
        f'''
        SELECT COUNT(*) AS total
        FROM checks c
        JOIN users u ON u.id = c.userId
        {where_sql}
        ''',
        params,
    ).fetchone()
    total = int(total_row['total']) if total_row else 0

    offset = (page - 1) * page_size
    rows = db.execute(
        f'''
        SELECT c.*, u.name AS authorName, u.email AS authorEmail
        FROM checks c
        JOIN users u ON u.id = c.userId
        {where_sql}
        ORDER BY c.{sort_by} {sort_dir.upper()}, c.id DESC
        LIMIT ? OFFSET ?
        ''',
        [*params, page_size, offset],
    ).fetchall()

    items = [_to_dto(r, request, include_text=False) for r in rows]
    return {'items': items, 'total': total, 'page': page, 'pageSize': page_size}


def get_check(db: sqlite3.Connection, request: Request, *, user: Dict[str, Any], check_id: str) -> Dict[str, Any]:
    row = db.execute(
        '''
        SELECT c.*, u.name AS authorName, u.email AS authorEmail
        FROM checks c
        JOIN users u ON u.id = c.userId
        WHERE c.id = ?
        ''',
        (check_id,),
    ).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'check not found')
    _assert_can_read(user, row)
    request.state.db = db
    return _to_dto(row, request, include_text=True)


def update_check(db: sqlite3.Connection, request: Request, *, user: Dict[str, Any], check_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    row = db.execute('SELECT * FROM checks WHERE id = ?', (check_id,)).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'check not found')
    _assert_can_update(user, row)

    label = patch.get('label') if patch is not None else None
    notes = patch.get('notes') if patch is not None else None

    if label is not None:
        label = str(label).strip()
        if len(label) < 2 or len(label) > 120:
            raise ApiError(400, 'VALIDATION_ERROR', 'label must be 2..120 chars')

    if notes is not None:
        notes = str(notes)
        if len(notes) > 4000:
            raise ApiError(400, 'VALIDATION_ERROR', 'notes max length is 4000 chars')

    db.execute(
        '''
        UPDATE checks
        SET label = COALESCE(?, label),
            notes = COALESCE(?, notes),
            updatedAt = ?
        WHERE id = ?
        ''',
        (label, notes, now_ms(), check_id),
    )
    db.commit()

    updated = db.execute(
        '''
        SELECT c.*, u.name AS authorName, u.email AS authorEmail
        FROM checks c
        JOIN users u ON u.id = c.userId
        WHERE c.id = ?
        ''',
        (check_id,),
    ).fetchone()

    request.state.db = db
    return _to_dto(updated, request, include_text=True)


def delete_check(db: sqlite3.Connection, *, user: Dict[str, Any], check_id: str) -> Dict[str, Any]:
    row = db.execute('SELECT id, userId FROM checks WHERE id = ?', (check_id,)).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'check not found')
    _assert_can_delete(user, row)

    files = db.execute('SELECT storageKey FROM attachments WHERE checkId = ?', (check_id,)).fetchall()
    db.execute('DELETE FROM attachments WHERE checkId = ?', (check_id,))
    db.execute('DELETE FROM checks WHERE id = ?', (check_id,))
    db.commit()

    for f in files:
        delete_object(f['storageKey'])

    return {'deleted': check_id}


def add_attachment(db: sqlite3.Connection, request: Request, *, user: Dict[str, Any], check_id: str, file: UploadFile) -> Dict[str, Any]:
    row = db.execute('SELECT * FROM checks WHERE id = ?', (check_id,)).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'check not found')
    _assert_can_update(user, row)

    attachment_id = make_id('att')
    content = file.file.read()
    stored = store_bytes(content, attachment_id=attachment_id, original_name=str(file.filename or 'attachment'), content_type=str(file.content_type or 'application/octet-stream'))
    created_at = now_ms()
    db.execute(
        '''
        INSERT INTO attachments (id, checkId, userId, originalName, storageKey, contentType, size, createdAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (attachment_id, check_id, user['id'], stored.original_name, stored.storage_key, stored.content_type, stored.size, created_at),
    )
    db.commit()
    request.state.db = db
    return _attachments_for_check(db, check_id, request)[0]


def delete_attachment(db: sqlite3.Connection, *, user: Dict[str, Any], check_id: str, attachment_id: str) -> Dict[str, Any]:
    row = db.execute(
        '''
        SELECT a.id, a.storageKey, c.userId
        FROM attachments a
        JOIN checks c ON c.id = a.checkId
        WHERE a.id = ? AND a.checkId = ?
        ''',
        (attachment_id, check_id),
    ).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'attachment not found')

    proxy_row = {'id': check_id, 'userId': row['userId']}
    _assert_can_update(user, proxy_row)
    db.execute('DELETE FROM attachments WHERE id = ?', (attachment_id,))
    db.commit()
    delete_object(row['storageKey'])
    return {'deleted': attachment_id}


def get_attachment_file(db: sqlite3.Connection, *, attachment_id: str, token: str) -> Dict[str, Any]:
    verify_signed_token(attachment_id, token)
    row = db.execute(
        '''
        SELECT id, originalName, storageKey, contentType
        FROM attachments
        WHERE id = ?
        ''',
        (attachment_id,),
    ).fetchone()
    if not row:
        raise ApiError(404, 'NOT_FOUND', 'attachment not found')
    target = resolve_download_target(row['storageKey'])
    return {
        'id': row['id'],
        'originalName': row['originalName'],
        'storageKey': row['storageKey'],
        'contentType': row['contentType'],
        **target,
    }
