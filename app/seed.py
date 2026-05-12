from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AdminUser
from .security import hash_password


DEFAULT_USERS = [
    {
        "name": "Studio admin",
        "username": "studio",
        "email": "studio@bichil.mn",
        "password": "studio123",
        "role": "edit_admin",
        "branch": "Төв салбар",
    },
    {
        "name": "Төв Админ",
        "username": "admin",
        "email": "admin@bichil.mn",
        "password": "admin123",
        "role": "super_admin",
        "branch": "Төв салбар",
    },
    {
        "name": "Салбар Админ",
        "username": "branch",
        "email": "branch@bichil.mn",
        "password": "branch123",
        "role": "branch_admin",
        "branch": "Салбар 1",
    },
    {
        "name": "Шууд Админ",
        "username": "direct",
        "email": "direct@bichil.mn",
        "password": "direct123",
        "role": "direct_admin",
        "branch": "Төв салбар",
    },
]


def seed_default_users(db: Session) -> None:
    for item in DEFAULT_USERS:
        existing = db.scalar(
            select(AdminUser).where(AdminUser.username == item["username"])
        )
        if existing:
            existing.name = item["name"]
            existing.email = item["email"]
            existing.password_hash = hash_password(item["password"])
            existing.role = item["role"]
            existing.branch = item["branch"]
            existing.status = "Active"
            existing.is_deleted = False
            continue

        db.add(
            AdminUser(
                name=item["name"],
                username=item["username"],
                email=item["email"],
                password_hash=hash_password(item["password"]),
                role=item["role"],
                branch=item["branch"],
                status="Active",
            )
        )
    db.commit()
