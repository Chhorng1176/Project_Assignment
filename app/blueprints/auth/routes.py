# app/blueprints/auth/routes.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)
from werkzeug.security import check_password_hash

from app.extensions import db
from app.models.user import User
from app.models.role import Role
from app.forms.auth_forms import LoginForm, RegisterForm


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)

# ==================================================
# LOGIN
# ==================================================
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # 🔐 Already logged in → let main router decide
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data
        ).first()

        # ❌ Invalid username or password
        if not user or not check_password_hash(
            user.password_hash,
            form.password.data
        ):
            flash("❌ Invalid username or password", "danger")
            return render_template(
                "auth/login.html",
                form=form
            )

        # 🚫 BANNED USER CHECK
        if not user.is_active:
            flash(
                "🚫 Your account has been banned. Please contact administrator.",
                "danger"
            )
            return render_template(
                "auth/login.html",
                form=form
            )

        # ✅ Login success
        login_user(user)
        flash("✅ Welcome back!", "success")

        # 🔁 Centralized redirect (role-based in main.index)
        return redirect(url_for("main.index"))

    return render_template(
        "auth/login.html",
        form=form
    )


# ==================================================
# REGISTER (FARMER ONLY)
# ==================================================
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # 🔐 Block logged-in users
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()

    if form.validate_on_submit():
        # ❌ Username exists
        if User.query.filter_by(username=form.username.data).first():
            flash("❌ Username already exists", "danger")
            return render_template(
                "auth/register.html",
                form=form
            )

        # ✅ Create farmer user
        user = User(username=form.username.data)
        user.set_password(form.password.data)

        farmer_role = Role.query.filter_by(name="farmer").first()
        if not farmer_role:
            flash(
                "❌ Farmer role not found. Contact admin.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        user.roles.append(farmer_role)

        db.session.add(user)
        db.session.commit()

        flash("✅ Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        form=form
    )


# ==================================================
# LOGOUT
# ==================================================
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("ℹ️ Logged out successfully", "info")
    return redirect(url_for("auth.login"))
