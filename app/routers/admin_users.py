from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_super_admin
from ..models import AdminUser
from ..schemas import AdminUserCreate, AdminUserOut, AdminUserUpdate
from ..security import hash_password
from .auth import to_user_out


router = APIRouter(prefix="/admin/users", tags=["admin-users"])


def get_user_or_404(user_id: int, db: Session) -> AdminUser:
    user = db.scalar(
        select(AdminUser).where(
            AdminUser.id == user_id,
            AdminUser.is_deleted.is_(False),
        )
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def ensure_unique(db: Session, *, username: str | None, email: str | None, user_id: int | None = None) -> None:
    if username:
        query = select(AdminUser).where(
            func.lower(AdminUser.username) == username.lower(),
            AdminUser.is_deleted.is_(False),
        )
        existing = db.scalar(query)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Энэ нэвтрэх нэр бүртгэлтэй байна.",
            )

    if email:
        query = select(AdminUser).where(
            func.lower(AdminUser.email) == email.lower(),
            AdminUser.is_deleted.is_(False),
        )
        existing = db.scalar(query)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Энэ имэйл бүртгэлтэй байна.",
            )


@router.get("", response_model=list[AdminUserOut])
def list_users(
    _: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> list[AdminUserOut]:
    users = db.scalars(
        select(AdminUser)
        .where(AdminUser.is_deleted.is_(False))
        .order_by(AdminUser.created_at.desc(), AdminUser.id.desc())
    ).all()
    return [to_user_out(user) for user in users]


@router.post("", response_model=AdminUserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate,
    _: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminUserOut:
    ensure_unique(db, username=payload.username, email=str(payload.email))
    user = AdminUser(
        name=payload.name,
        username=payload.username,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        role=payload.role,
        branch=payload.branch,
        status=payload.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return to_user_out(user)


@router.patch("/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    _: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminUserOut:
    user = get_user_or_404(user_id, db)
    changes = payload.model_dump(exclude_unset=True)

    email_value = changes.get("email")
    ensure_unique(
        db,
        username=changes.get("username"),
        email=str(email_value) if email_value is not None else None,
        user_id=user.id,
    )

    password = changes.pop("password", None)
    if password:
        user.password_hash = hash_password(password)

    for key, value in changes.items():
        if value is not None:
            setattr(user, key, str(value) if key == "email" else value)

    db.commit()
    db.refresh(user)
    return to_user_out(user)


@router.patch("/{user_id}/block", response_model=AdminUserOut)
def toggle_block_user(
    user_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminUserOut:
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Өөрийн эрхийг block хийх боломжгүй.",
        )

    user = get_user_or_404(user_id, db)
    user.status = "Active" if user.status == "Blocked" else "Blocked"
    db.commit()
    db.refresh(user)
    return to_user_out(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: AdminUser = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> None:
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Өөрийн эрхийг устгах боломжгүй.",
        )

    user = get_user_or_404(user_id, db)
    db.delete(user)
    db.commit()
