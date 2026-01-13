# app/blueprints/admin/routes.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import login_required, current_user

from app.extensions import db
from app.utils.decorators import permission_required

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.audit_log import AuditLog
from app.models.diagnosis import Diagnosis
from app.models.chat_message import ChatMessage


admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin"
)

# ==================================================
# ADMIN DASHBOARD
# ==================================================
@admin_bp.route("/dashboard")
@login_required
@permission_required("view_dashboard")
def dashboard():
    return render_template(
        "admin/dashboard.html",
        total_users=User.query.count(),
        active_users=User.query.filter_by(is_active=True).count(),
        banned_users=User.query.filter_by(is_active=False).count(),
        total_diagnoses=Diagnosis.query.count(),
        pending_diagnoses=Diagnosis.query.filter_by(status="PENDING").count(),
        total_chats=ChatMessage.query.count()
    )


# ==================================================
# 📊 EXPERT STATISTICS
# ==================================================
@admin_bp.route("/expert-statistics")
@login_required
@permission_required("view_reports")
def expert_statistics():
    return render_template(
        "admin/expert_stats.html",
        total_diagnoses=Diagnosis.query.count(),
        pending_diagnoses=Diagnosis.query.filter_by(status="PENDING").count(),
        reviewed_diagnoses=Diagnosis.query.filter(
            Diagnosis.status != "PENDING"
        ).count(),
        total_chats=ChatMessage.query.count()
    )


# ==================================================
# USER MANAGEMENT
# ==================================================
@admin_bp.route("/users")
@login_required
@permission_required("manage_users")
def users():
    return render_template(
        "admin/users.html",
        users=User.query.order_by(User.created_at.desc()).all(),
        roles=Role.query.all()
    )


# ==================================================
# CREATE USER
# ==================================================
@admin_bp.route("/users/create", methods=["POST"])
@login_required
@permission_required("manage_users")
def create_user():
    username = request.form.get("username")
    password = request.form.get("password")
    role_name = request.form.get("role")

    if not username or not password or not role_name:
        flash("❌ All fields are required", "danger")
        return redirect(url_for("admin.users"))

    if User.query.filter_by(username=username).first():
        flash("❌ Username already exists", "danger")
        return redirect(url_for("admin.users"))

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        flash("❌ Invalid role", "danger")
        return redirect(url_for("admin.users"))

    user = User(username=username)
    user.set_password(password)
    user.roles.append(role)

    db.session.add(user)
    db.session.flush()

    db.session.add(
        AuditLog(
            user_id=current_user.id,
            action="CREATE_USER",
            target_user=username,
            detail=f"role={role_name}"
        )
    )

    db.session.commit()
    flash("✅ User created successfully", "success")
    return redirect(url_for("admin.users"))


# ==================================================
# BAN / UNBAN USER
# ==================================================
@admin_bp.route("/users/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@permission_required("manage_users")
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)

    if user.has_role("admin"):
        flash("❌ Cannot ban admin account", "danger")
        return redirect(url_for("admin.users"))

    user.is_active = not user.is_active

    db.session.add(
        AuditLog(
            user_id=current_user.id,
            action="BAN_USER" if not user.is_active else "UNBAN_USER",
            target_user=user.username,
            detail=f"is_active={user.is_active}"
        )
    )

    db.session.commit()
    flash("⚠️ User status updated", "warning")
    return redirect(url_for("admin.users"))


# ==================================================
# CHANGE USER ROLE
# ==================================================
@admin_bp.route("/users/<int:user_id>/change-role", methods=["POST"])
@login_required
@permission_required("manage_users")
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")

    role = Role.query.filter_by(name=new_role).first()
    if not role:
        flash("❌ Invalid role", "danger")
        return redirect(url_for("admin.users"))

    old_roles = [r.name for r in user.roles]

    user.roles.clear()
    user.roles.append(role)

    db.session.add(
        AuditLog(
            user_id=current_user.id,
            action="CHANGE_ROLE",
            target_user=user.username,
            detail=f"{old_roles} → {new_role}"
        )
    )

    db.session.commit()
    flash("✅ Role updated", "success")
    return redirect(url_for("admin.users"))


# ==================================================
# ROLE LIST
# ==================================================
@admin_bp.route("/roles")
@login_required
@permission_required("manage_roles")
def roles():
    return render_template(
        "admin/roles.html",
        roles=Role.query.all()
    )


# ==================================================
# ROLE PERMISSIONS  ✅ REQUIRED FIX
# ==================================================
@admin_bp.route("/roles/<int:role_id>/permissions", methods=["GET", "POST"])
@login_required
@permission_required("manage_roles")
def manage_role_permissions(role_id):
    role = Role.query.get_or_404(role_id)
    permissions = Permission.query.all()

    if request.method == "POST":
        role.permissions.clear()

        for pid in request.form.getlist("permissions"):
            perm = Permission.query.get(int(pid))
            if perm:
                role.permissions.append(perm)

        # 🔐 Protect admin core permissions
        if role.name == "admin":
            for code in ["view_dashboard", "manage_users", "manage_roles"]:
                perm = Permission.query.filter_by(code=code).first()
                if perm and perm not in role.permissions:
                    role.permissions.append(perm)

        db.session.add(
            AuditLog(
                user_id=current_user.id,
                action="UPDATE_ROLE_PERMISSIONS",
                target_user=role.name
            )
        )

        db.session.commit()
        flash("✅ Permissions updated", "success")
        return redirect(url_for("admin.roles"))

    return render_template(
        "admin/role_permissions.html",
        role=role,
        permissions=permissions
    )


# ==================================================
# 🔍 AUDIT LOGS
# ==================================================
@admin_bp.route("/audit-logs")
@login_required
@permission_required("view_dashboard")
def audit_logs():
    logs = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )

    return render_template(
        "admin/audit_logs.html",
        logs=logs
    )
