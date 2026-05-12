from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AdminUser, SiteConfig
from ..schemas import SiteConfigPayload, SiteConfigResponse


router = APIRouter(tags=["site-config"])
ACTIVE_CONFIG_KEY = "active"


def get_active_config(db: Session) -> SiteConfig | None:
    return db.scalar(select(SiteConfig).where(SiteConfig.key == ACTIVE_CONFIG_KEY))


@router.get("/public-config", response_model=SiteConfigResponse)
def get_public_config(db: Session = Depends(get_db)) -> SiteConfigResponse:
    config = get_active_config(db)
    return SiteConfigResponse(config=config.config if config else None)


@router.put("/admin-config", response_model=SiteConfigResponse)
def save_admin_config(
    payload: SiteConfigPayload,
    _: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SiteConfigResponse:
    config = get_active_config(db)

    if config:
        config.config = payload.config
    else:
        config = SiteConfig(key=ACTIVE_CONFIG_KEY, config=payload.config)
        db.add(config)

    db.commit()
    db.refresh(config)
    return SiteConfigResponse(config=config.config)
