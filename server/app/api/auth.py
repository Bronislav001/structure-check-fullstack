from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlite3 import Connection

from ..db import get_db
from ..dependencies import get_current_user
from ..models import AuthOut, LoginIn, LogoutIn, LogoutOut, MeOut, RefreshIn, RegisterIn
from ..services.auth import login_user, logout_session, refresh_session, register_user


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthOut, status_code=201)
def register(payload: RegisterIn, db: Connection = Depends(get_db)):
    return register_user(db, email=payload.email, name=payload.name, password=payload.password)


@router.post("/login", response_model=AuthOut)
def login(payload: LoginIn, db: Connection = Depends(get_db)):
    return login_user(db, email=payload.email, password=payload.password)


@router.post("/refresh", response_model=AuthOut)
def refresh(payload: RefreshIn, db: Connection = Depends(get_db)):
    return refresh_session(db, refresh_token=payload.refreshToken)


@router.post("/logout", response_model=LogoutOut)
def logout(payload: LogoutIn, db: Connection = Depends(get_db)):
    return logout_session(db, refresh_token=payload.refreshToken)


@router.get("/me", response_model=MeOut)
def me(user=Depends(get_current_user)):
    return {"user": user}
