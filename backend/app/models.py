from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False)


class AccessRequest(Base):
    __tablename__ = "access_requests"

    id = Column(Integer, primary_key=True, index=True)
    teleport_request_id = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=False)
    resource = Column(String(255), nullable=False)
    role_requested = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    ticket_id = Column(String(64), nullable=False)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    session_start = Column(DateTime, nullable=True)
    session_end = Column(DateTime, nullable=True)
    commands_executed = Column(Text, nullable=True)

    approvals = relationship("Approval", back_populates="request", cascade="all, delete-orphan")


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("access_requests.id"), nullable=False)
    approver = Column(String(128), nullable=False)
    approved_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("AccessRequest", back_populates="approvals")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(128), nullable=False)
    action = Column(String(128), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
