import os
from datetime import datetime
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import create_access_token, hash_password, verify_password, require_roles
from .database import Base, engine, get_db
from .models import AccessRequest, Approval, AuditLog, User
from .schemas import (
    AccessRequestList,
    AccessRequestOut,
    ActionResponse,
    ApproveResponse,
    AuditLogOut,
    CreateRequestIn,
    LoginRequest,
    TokenResponse,
)
from .services import (
    approve_teleport_request,
    create_teleport_request,
    deny_teleport_request,
    send_slack_notification,
    validate_ticket,
)

REQUIRED_APPROVALS = int(os.getenv("REQUIRED_APPROVALS", "2"))

app = FastAPI(title="Teleport PAM Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    seed_users = [
        ("dev1", "developer"),
        ("admin1", "admin"),
        ("sec1", "security"),
    ]
    for username, role in seed_users:
        if not db.query(User).filter(User.username == username).first():
            db.add(User(username=username, password_hash=hash_password("changeme"), role=role))
    db.commit()


def write_audit(db: Session, actor: str, action: str, details: str) -> None:
    db.add(AuditLog(actor=actor, action=action, details=details))
    db.commit()


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.username, user.role)
    return TokenResponse(access_token=token, role=user.role)


@app.post("/requests/create", response_model=AccessRequestOut)
def create_request(
    payload: CreateRequestIn,
    current=Depends(require_roles("developer", "admin")),
    db: Session = Depends(get_db),
):
    if not payload.ticket_id:
        raise HTTPException(status_code=400, detail="ticket_id is required")
    if not validate_ticket(payload.ticket_id):
        raise HTTPException(status_code=400, detail="Invalid ticket ID")

    teleport_id = create_teleport_request(payload.role_requested, payload.reason)

    request_row = AccessRequest(
        teleport_request_id=teleport_id,
        username=current["username"],
        resource=payload.resource,
        role_requested=payload.role_requested,
        reason=payload.reason,
        ticket_id=payload.ticket_id,
        status="pending",
    )
    db.add(request_row)
    db.commit()
    db.refresh(request_row)

    portal_base = os.getenv("PORTAL_BASE_URL", "http://localhost:5173")
    message = (
        f"User: {request_row.username}\n"
        f"Requested Role: {request_row.role_requested}\n"
        f"Server: {request_row.resource}\n"
        f"Reason: {request_row.reason}\n"
        f"Approve URL: {portal_base}/admin"
    )
    send_slack_notification(message)
    write_audit(db, current["username"], "request_created", f"request_id={request_row.id}")

    return AccessRequestOut(
        **request_row.__dict__, approvals_count=0
    )


@app.get("/requests", response_model=AccessRequestList)
def list_requests(current=Depends(require_roles("developer", "admin", "security")), db: Session = Depends(get_db)):
    if current["role"] == "developer":
        requests = db.query(AccessRequest).filter(AccessRequest.username == current["username"]).order_by(AccessRequest.created_at.desc()).all()
    else:
        requests = db.query(AccessRequest).order_by(AccessRequest.created_at.desc()).all()
    output = [
        AccessRequestOut(**r.__dict__, approvals_count=len(r.approvals))
        for r in requests
    ]
    return AccessRequestList(requests=output)


@app.post("/requests/{request_id}/approve", response_model=ApproveResponse)
def approve_request(request_id: int, current=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    request_row = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request_row:
        raise HTTPException(status_code=404, detail="Request not found")
    if request_row.status != "pending":
        raise HTTPException(status_code=400, detail="Request is not pending")

    existing = db.query(Approval).filter(Approval.request_id == request_id, Approval.approver == current["username"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already approved by this user")

    db.add(Approval(request_id=request_id, approver=current["username"]))
    db.commit()

    approvals_count = db.query(Approval).filter(Approval.request_id == request_id).count()
    status = "pending"
    if approvals_count >= REQUIRED_APPROVALS:
        approve_teleport_request(request_row.teleport_request_id)
        request_row.status = "approved"
        request_row.approved_at = datetime.utcnow()
        db.commit()
        status = "approved"

    write_audit(db, current["username"], "request_approved", f"request_id={request_id},count={approvals_count}")
    return ApproveResponse(
        message="Approval recorded",
        approvals_count=approvals_count,
        required_approvals=REQUIRED_APPROVALS,
        status=status,
    )


@app.post("/requests/{request_id}/deny", response_model=ActionResponse)
def deny_request(request_id: int, current=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    request_row = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
    if not request_row:
        raise HTTPException(status_code=404, detail="Request not found")
    if request_row.status != "pending":
        raise HTTPException(status_code=400, detail="Request is not pending")
    deny_teleport_request(request_row.teleport_request_id)
    request_row.status = "denied"
    db.commit()
    write_audit(db, current["username"], "request_denied", f"request_id={request_id}")
    return ActionResponse(message="Request denied")


@app.get("/audit/logs", response_model=list[AuditLogOut])
def get_audit_logs(current=Depends(require_roles("security", "admin")), db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).all()
    return [AuditLogOut(actor=l.actor, action=l.action, details=l.details, created_at=l.created_at) for l in logs]
