import asyncio
import json
from queue import Empty, Queue

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import AdminUser, FeedbackRequest
from ..schemas import FeedbackRequestCreate, FeedbackRequestOut, FeedbackRequestUpdate
from ..security import decode_access_token


router = APIRouter(prefix="/feedback-requests", tags=["feedback-requests"])
subscribers: set[Queue[str]] = set()


def format_created_at(request: FeedbackRequest) -> str:
    if not request.created_at:
        return ""
    return request.created_at.strftime("%Y-%m-%d, %H:%M")


def to_request_out(request: FeedbackRequest) -> FeedbackRequestOut:
    return FeedbackRequestOut(
        id=request.id,
        user=request.customer_name,
        phone=request.phone,
        type=request.request_type,
        targetType=request.target_type,
        employeeName=request.employee_name,
        desc=request.description,
        branch=request.branch,
        status=request.status,
        created_at=format_created_at(request),
        assigned_at=request.assigned_at,
        resolved_at=request.resolved_at,
        returned_at=request.returned_at,
        isDirect=request.is_direct,
        isOperator=request.is_operator,
        rating=request.rating,
        file=request.file_name,
        recipient=request.recipient,
        resolution=request.resolution,
    )


def serialize_event(event_type: str, request: FeedbackRequest) -> str:
    payload = {
        "event": event_type,
        "request": to_request_out(request).model_dump(),
    }
    return json.dumps(payload, ensure_ascii=False)


def broadcast_request_event(event_type: str, request: FeedbackRequest) -> None:
    message = serialize_event(event_type, request)
    for subscriber in list(subscribers):
        subscriber.put_nowait(message)


def validate_stream_user(token: str | None, db: Session) -> AdminUser:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.get(AdminUser, int(payload["sub"]))
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
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
    return user


async def feedback_event_stream(request: Request, subscriber: Queue[str]):
    try:
        yield "event: ready\ndata: {}\n\n"
        while True:
            if await request.is_disconnected():
                break

            try:
                message = await asyncio.to_thread(subscriber.get, True, 15)
                yield f"event: feedback\ndata: {message}\n\n"
            except Empty:
                yield "event: ping\ndata: {}\n\n"
    finally:
        subscribers.discard(subscriber)


@router.post("", response_model=FeedbackRequestOut, status_code=status.HTTP_201_CREATED)
def create_feedback_request(
    payload: FeedbackRequestCreate,
    db: Session = Depends(get_db),
) -> FeedbackRequestOut:
    request = FeedbackRequest(
        customer_name=payload.user.strip(),
        phone=payload.phone.strip() if payload.phone else None,
        request_type=payload.type,
        target_type=payload.targetType,
        employee_name=payload.employeeName.strip() if payload.employeeName else None,
        description=payload.desc.strip(),
        branch=payload.branch.strip() if payload.branch else None,
        status="Pending",
        is_direct=payload.isDirect,
        is_operator=payload.isOperator,
        rating=payload.rating,
        file_name=payload.file.strip() if payload.file else None,
        recipient=payload.recipient.strip() if payload.recipient else None,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    broadcast_request_event("created", request)
    return to_request_out(request)


@router.get("", response_model=list[FeedbackRequestOut])
def list_feedback_requests(
    _: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[FeedbackRequestOut]:
    requests = db.scalars(
        select(FeedbackRequest).order_by(
            FeedbackRequest.created_at.desc(),
            FeedbackRequest.id.desc(),
        )
    ).all()
    return [to_request_out(request) for request in requests]


@router.get("/stream")
def stream_feedback_requests(
    request: Request,
    token: str | None = None,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    validate_stream_user(token, db)
    subscriber: Queue[str] = Queue()
    subscribers.add(subscriber)
    return StreamingResponse(
        feedback_event_stream(request, subscriber),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.patch("/{request_id}", response_model=FeedbackRequestOut)
def update_feedback_request(
    request_id: int,
    payload: FeedbackRequestUpdate,
    _: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FeedbackRequestOut:
    request = db.get(FeedbackRequest, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        if key == "branch":
            request.branch = value
        elif value is not None:
            setattr(request, key, value)

    db.commit()
    db.refresh(request)
    broadcast_request_event("updated", request)
    return to_request_out(request)
