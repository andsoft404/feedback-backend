from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(260), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    branch: Mapped[str] = mapped_column(String(160), nullable=False, default="Төв салбар")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="Active", index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class FeedbackRequest(Base):
    __tablename__ = "feedback_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    request_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(40), nullable=False, default="Organization")
    employee_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    branch: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Pending", index=True)
    is_direct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_operator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_name: Mapped[str | None] = mapped_column(String(260), nullable=True)
    recipient: Mapped[str | None] = mapped_column(String(160), nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    resolved_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    returned_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SiteConfig(Base):
    __tablename__ = "site_configs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    config: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
