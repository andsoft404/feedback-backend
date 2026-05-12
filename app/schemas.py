from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


ROLE_VALUES = {"super_admin", "branch_admin", "direct_admin", "edit_admin"}
STATUS_VALUES = {"Active", "Inactive", "Blocked"}


def destination_for_role(role: str) -> str:
    return "studio" if role == "edit_admin" else "front"


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=160)


class AdminUserBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    username: str = Field(min_length=1, max_length=80)
    email: EmailStr
    role: str
    branch: str = Field(min_length=1, max_length=160)
    status: str = "Active"

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        if value not in ROLE_VALUES:
            raise ValueError("Invalid role")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in STATUS_VALUES:
            raise ValueError("Invalid status")
        return value


class AdminUserCreate(AdminUserBase):
    password: str = Field(min_length=6, max_length=160)


class AdminUserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    username: str | None = Field(default=None, min_length=1, max_length=80)
    email: EmailStr | None = None
    role: str | None = None
    branch: str | None = Field(default=None, min_length=1, max_length=160)
    status: str | None = None
    password: str | None = Field(default=None, min_length=6, max_length=160)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str | None) -> str | None:
        return value.strip().lower() if value else value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is not None and value not in ROLE_VALUES:
            raise ValueError("Invalid role")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in STATUS_VALUES:
            raise ValueError("Invalid status")
        return value


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: EmailStr
    role: str
    branch: str
    status: str
    destination: str


class LoginUserOut(AdminUserOut):
    pass


class LoginResponse(BaseModel):
    token: str
    user: LoginUserOut


REQUEST_TYPE_VALUES = {"Хүсэлт", "Гомдол", "Талархал"}
REQUEST_TARGET_VALUES = {"Organization", "Employee"}
REQUEST_STATUS_VALUES = {"Pending", "Assigned", "Processing", "Resolved", "Returned", "Rejected"}


class FeedbackRequestCreate(BaseModel):
    user: str = Field(min_length=1, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    type: str
    targetType: str = "Organization"
    employeeName: str | None = Field(default=None, max_length=160)
    desc: str = Field(min_length=1, max_length=5000)
    branch: str | None = Field(default=None, max_length=160)
    isDirect: bool = False
    isOperator: bool = False
    rating: int = Field(default=0, ge=0, le=5)
    file: str | None = Field(default=None, max_length=260)
    recipient: str | None = Field(default=None, max_length=160)

    @field_validator("type")
    @classmethod
    def validate_request_type(cls, value: str) -> str:
        if value not in REQUEST_TYPE_VALUES:
            raise ValueError("Invalid request type")
        return value

    @field_validator("targetType")
    @classmethod
    def validate_target_type(cls, value: str) -> str:
        if value not in REQUEST_TARGET_VALUES:
            raise ValueError("Invalid target type")
        return value


class FeedbackRequestUpdate(BaseModel):
    branch: str | None = Field(default=None, max_length=160)
    status: str | None = None
    resolution: str | None = Field(default=None, max_length=5000)
    assigned_at: str | None = Field(default=None, max_length=40)
    resolved_at: str | None = Field(default=None, max_length=40)
    returned_at: str | None = Field(default=None, max_length=40)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is not None and value not in REQUEST_STATUS_VALUES:
            raise ValueError("Invalid status")
        return value


class FeedbackRequestOut(BaseModel):
    id: int
    user: str
    phone: str | None
    type: str
    targetType: str
    employeeName: str | None
    desc: str
    branch: str | None
    status: str
    created_at: str
    assigned_at: str | None
    resolved_at: str | None
    returned_at: str | None
    isDirect: bool
    isOperator: bool
    rating: int
    file: str | None
    recipient: str | None
    resolution: str | None


class SiteConfigPayload(BaseModel):
    config: dict[str, Any]


class SiteConfigResponse(BaseModel):
    config: dict[str, Any] | None = None
