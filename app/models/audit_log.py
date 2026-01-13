# app/models/audit_log.py

from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    # Who did the action (admin)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Action type (CREATE_USER, BAN_USER, CHANGE_ROLE, ...)
    action = db.Column(
        db.String(100),
        nullable=False
    )

    # Target username / role / object
    target_user = db.Column(
        db.String(100),
        nullable=True
    )

    # Extra detail (role change, status, etc.)
    detail = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationship
    user = db.relationship("User")

    def __repr__(self):
        return (
            f"<AuditLog action={self.action} "
            f"user_id={self.user_id} "
            f"target={self.target_user}>"
        )
