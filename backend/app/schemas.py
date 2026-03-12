from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class CreateRequestIn(BaseModel):
    resource: str
    role_requested: str
    reason: str
    ticket_id: str


class AccessRequestOut(BaseModel):
    id: int
    teleport_request_id: str
    username: str
    resource: str
    role_requested: str
    reason: str
    ticket_id: str
    status: str
    created_at: datetime
    approved_at: Optional[datetime]
    approvals_count: int


class ActionResponse(BaseModel):
    message: str


class AuditLogOut(BaseModel):
    actor: str
    action: str
    details: Optional[str]
    created_at: datetime


class ApproveResponse(BaseModel):
    message: str
    approvals_count: int
    required_approvals: int
    status: str


class AccessRequestList(BaseModel):
    requests: List[AccessRequestOut]
