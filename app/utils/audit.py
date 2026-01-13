# app/utils/audit.py

from app.extensions import db
from app.models.audit_log import AuditLog


def log_action(admin, action, target_user=None, detail=None):
    log = AuditLog(
        admin_id=admin.id,
        admin_username=admin.username,
        action=action,
        target_user=target_user,
        detail=detail
    )
    db.session.add(log)
    db.session.commit()
