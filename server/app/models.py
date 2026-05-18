from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: str
    email: str
    name: str
    role: str


class RegisterIn(BaseModel):
    email: str
    name: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refreshToken: str


class LogoutIn(BaseModel):
    refreshToken: str


class AuthOut(BaseModel):
    user: UserPublic
    accessToken: str
    refreshToken: str
    accessTokenExpiresIn: int


class LogoutOut(BaseModel):
    ok: bool


class MeOut(BaseModel):
    user: UserPublic


class UsersListOut(BaseModel):
    items: List[UserPublic]


class RolePatchIn(BaseModel):
    role: str


class RolePatchOut(BaseModel):
    user: UserPublic


class CheckCreateIn(BaseModel):
    label: str = Field(min_length=2, max_length=120)
    text: str = Field(min_length=10)
    notes: str = Field(default='', max_length=4000)


class CheckPatchIn(BaseModel):
    label: Optional[str] = Field(default=None, min_length=2, max_length=120)
    notes: Optional[str] = Field(default=None, max_length=4000)


class OrderIssue(BaseModel):
    type: str
    message: str
    section: str


class AttachmentOut(BaseModel):
    id: str
    checkId: str
    originalName: str
    contentType: str
    size: int
    createdAt: int
    downloadUrl: str


class CheckOut(BaseModel):
    id: str
    userId: str
    authorName: Optional[str] = None
    authorEmail: Optional[str] = None
    label: str
    text: Optional[str] = None
    notes: str
    createdAt: int
    updatedAt: int
    inputLength: int
    ok: bool
    template: List[str]
    found: List[str]
    missing: List[str]
    orderIssues: List[OrderIssue]
    attachments: List[AttachmentOut] = Field(default_factory=list)


class ChecksListOut(BaseModel):
    items: List[CheckOut]
    total: int
    page: int
    pageSize: int


class DeleteOut(BaseModel):
    deleted: str


class CheckFiltersOut(BaseModel):
    q: str = ''
    status: Literal['all', 'ok', 'issues'] = 'all'
    sortBy: Literal['createdAt', 'updatedAt', 'label'] = 'createdAt'
    sortDir: Literal['asc', 'desc'] = 'desc'
    page: int = 1
    pageSize: int = 5
    scope: Literal['own', 'all'] = 'own'
    ownerId: str = ''


class SignedUrlOut(BaseModel):
    url: str
