from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlite3 import Connection

from ..db import get_db
from ..models import CheckCreateIn, CheckOut, CheckPatchIn, ChecksListOut, DeleteOut, AttachmentOut
from ..rbac import PERMS
from ..dependencies import require_permission
from ..services.checks import (
    add_attachment,
    create_check,
    create_check_from_upload,
    delete_attachment,
    delete_check,
    get_attachment_file,
    get_check,
    list_checks,
    update_check,
)


router = APIRouter(prefix='/api/checks', tags=['checks'])
files_router = APIRouter(prefix='/api/files', tags=['files'])


@router.get('/', response_model=ChecksListOut)
def list_(
    request: Request,
    scope: str | None = Query(default=None, pattern='^(all|own)?$'),
    q: str = Query(default=''),
    status: str = Query(default='all', pattern='^(all|ok|issues)$'),
    sortBy: str = Query(default='createdAt', pattern='^(createdAt|updatedAt|label)$'),
    sortDir: str = Query(default='desc', pattern='^(asc|desc)$'),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=5, ge=1, le=20),
    ownerId: str = Query(default=''),
    user=Depends(require_permission(PERMS.CHECKS_READ_OWN)),
    db: Connection = Depends(get_db),
):
    return list_checks(
        db,
        request,
        user=user,
        scope=(scope or '').strip() or None,
        q=q,
        status=status,
        sort_by=sortBy,
        sort_dir=sortDir,
        page=page,
        page_size=pageSize,
        owner_id=ownerId,
    )


@router.post('/', response_model=CheckOut, status_code=201)
def create(
    request: Request,
    payload: CheckCreateIn,
    user=Depends(require_permission(PERMS.CHECKS_CREATE)),
    db: Connection = Depends(get_db),
):
    return create_check(db, request, user_id=user['id'], label=payload.label, text=payload.text, notes=payload.notes)


@router.post('/from-upload', response_model=CheckOut, status_code=201)
def create_from_upload(
    request: Request,
    label: str = Form(...),
    notes: str = Form(default=''),
    upload: UploadFile = File(...),
    user=Depends(require_permission(PERMS.CHECKS_CREATE)),
    db: Connection = Depends(get_db),
):
    return create_check_from_upload(db, request, user_id=user['id'], label=label, notes=notes, file=upload)


@router.get('/{check_id}', response_model=CheckOut)
def get_one(
    request: Request,
    check_id: str,
    user=Depends(require_permission(PERMS.CHECKS_READ_OWN)),
    db: Connection = Depends(get_db),
):
    return get_check(db, request, user=user, check_id=check_id)


@router.patch('/{check_id}', response_model=CheckOut)
def patch(
    request: Request,
    check_id: str,
    payload: CheckPatchIn,
    user=Depends(require_permission(PERMS.CHECKS_UPDATE_OWN)),
    db: Connection = Depends(get_db),
):
    return update_check(db, request, user=user, check_id=check_id, patch=payload.model_dump(exclude_unset=True))


@router.delete('/{check_id}', response_model=DeleteOut)
def delete(
    check_id: str,
    user=Depends(require_permission(PERMS.CHECKS_DELETE_OWN)),
    db: Connection = Depends(get_db),
):
    return delete_check(db, user=user, check_id=check_id)


@router.post('/{check_id}/attachments', response_model=AttachmentOut, status_code=201)
def upload_attachment(
    request: Request,
    check_id: str,
    upload: UploadFile = File(...),
    user=Depends(require_permission(PERMS.CHECKS_UPDATE_OWN)),
    db: Connection = Depends(get_db),
):
    return add_attachment(db, request, user=user, check_id=check_id, file=upload)


@router.delete('/{check_id}/attachments/{attachment_id}', response_model=DeleteOut)
def remove_attachment(
    check_id: str,
    attachment_id: str,
    user=Depends(require_permission(PERMS.CHECKS_UPDATE_OWN)),
    db: Connection = Depends(get_db),
):
    return delete_attachment(db, user=user, check_id=check_id, attachment_id=attachment_id)


@files_router.get('/{attachment_id}')
def download_file(
    attachment_id: str,
    token: str = Query(...),
    db: Connection = Depends(get_db),
):
    data = get_attachment_file(db, attachment_id=attachment_id, token=token)
    if data.get('mode') == 'redirect':
        return RedirectResponse(url=data['url'], status_code=307)
    return FileResponse(data['path'], media_type=data['contentType'], filename=data['originalName'])
