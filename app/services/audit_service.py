from flask_login import current_user
from app.extensions import db
from app.models.audit_log import AuditLog

def log_action(action, target_type=None, target_id=None):
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        username=current_user.username if current_user.is_authenticated else "System",
        action=action,
        target_type=target_type,
        target_id=target_id
    )
    db.session.add(log)
    db.session.commit()
