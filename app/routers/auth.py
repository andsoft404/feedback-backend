from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AdminUser
from ..schemas import AdminUserOut, LoginRequest, LoginResponse, destination_for_role
from ..security import create_access_token, verify_password


router = APIRouter(tags=["auth"])


def to_user_out(user: AdminUser) -> AdminUserOut:
    return AdminUserOut(
        id=user.id,
        name=user.name,
        username=user.username,
        email=user.email,
        role=user.role,
        branch=user.branch,
        status=user.status,
        destination=destination_for_role(user.role),
    )


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    username = payload.username.strip().lower()
    user = db.scalar(
        select(AdminUser).where(
            func.lower(AdminUser.username) == username,
            AdminUser.is_deleted.is_(False),
        )
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Нэвтрэх нэр эсвэл нууц үг буруу байна.",
        )

    if user.status == "Blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Энэ эрх block хийгдсэн байна.",
        )

    if user.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Энэ эрх идэвхгүй байна.",
        )

    return LoginResponse(
        token=create_access_token(user.id, user.role),
        user=to_user_out(user),
    )


@router.get("/auth/me", response_model=AdminUserOut)
def me(current_user: AdminUser = Depends(get_current_user)) -> AdminUserOut:
    return to_user_out(current_user)
