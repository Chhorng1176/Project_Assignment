# app/models/user.py

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager
from .associations import user_roles


# ===============================
# FLASK-LOGIN USER LOADER
# ===============================
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login callback
    """
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None


# ===============================
# USER MODEL
# ===============================
class User(db.Model, UserMixin):
    __tablename__ = "users"

    # ===============================
    # PRIMARY KEY
    # ===============================
    id = db.Column(db.Integer, primary_key=True)

    # ===============================
    # AUTH FIELDS
    # ===============================
    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    # ===============================
    # ACCOUNT STATUS (BAN / ACTIVE)
    # ===============================
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # ===============================
    # TIMESTAMP
    # ===============================
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ===============================
    # RELATIONSHIPS
    # ===============================
    roles = db.relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="joined"
    )

    # ===============================
    # PASSWORD HELPERS
    # ===============================
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ===============================
    # ROLE CHECK
    # ===============================
    def has_role(self, role_name: str) -> bool:
        if not self.roles:
            return False
        return any(role.name == role_name for role in self.roles)

    # ===============================
    # PERMISSION CHECK
    # ===============================
    def has_permission(self, permission_code: str) -> bool:
        if not self.roles:
            return False

        for role in self.roles:
            for perm in getattr(role, "permissions", []):
                if perm.code == permission_code:
                    return True

        return False

    # ===============================
    # FLASK-LOGIN OVERRIDE
    # ===============================
    def get_id(self):
        return str(self.id)

    # ===============================
    # DEBUG
    # ===============================
    def __repr__(self):
        return f"<User id={self.id} username={self.username} active={self.is_active}>"
