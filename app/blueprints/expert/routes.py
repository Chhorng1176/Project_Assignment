# app/blueprints/expert/routes.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import current_user

from app.utils.decorators import role_required
from app.extensions import db

from app.models.diagnosis import Diagnosis
from app.models.chat_message import ChatMessage
from app.models.crop import Crop
from app.models.disease import Disease


# ===============================
# EXPERT BLUEPRINT
# ===============================
expert_bp = Blueprint(
    "expert",
    __name__,
    url_prefix="/expert"
)


# ===============================
# EXPERT DASHBOARD
# ===============================
@expert_bp.route("/dashboard")
@role_required("expert")
def dashboard():
    pending_diagnoses = (
        Diagnosis.query
        .filter_by(status="PENDING")
        .order_by(Diagnosis.created_at.desc())
        .all()
    )

    return render_template(
        "expert/dashboard.html",
        diagnoses=pending_diagnoses
    )


# ===============================
# REVIEW / APPROVE / REJECT DIAGNOSIS
# ===============================
@expert_bp.route("/diagnosis/<int:diagnosis_id>", methods=["GET", "POST"])
@role_required("expert")
def review_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "approve":
            solution = request.form.get("solution")

            if not solution:
                flash("❌ Solution is required", "danger")
                return redirect(request.url)

            diagnosis.approve(
                expert_id=current_user.id,
                solution=solution
            )
            db.session.commit()
            flash("✅ Diagnosis approved", "success")

        elif action == "reject":
            diagnosis.reject(expert_id=current_user.id)
            db.session.commit()
            flash("⚠️ Diagnosis rejected", "warning")

        return redirect(url_for("expert.dashboard"))

    return render_template(
        "expert/review_diagnosis.html",
        diagnosis=diagnosis
    )


# ===============================
# FARMER CHAT LIST (EXPERT VIEW)
# ===============================
@expert_bp.route("/farmer-chats")
@role_required("expert")
def farmer_chats():
    farmer_ids = (
        db.session.query(ChatMessage.farmer_id)
        .filter(ChatMessage.sender == "farmer")
        .distinct()
        .all()
    )

    farmer_ids = [fid[0] for fid in farmer_ids if fid[0]]

    return render_template(
        "expert/farmer_chats.html",
        farmer_ids=farmer_ids
    )


# ===============================
# EXPERT REPLY CHAT
# ===============================
@expert_bp.route("/chat/<int:farmer_id>", methods=["GET", "POST"])
@role_required("expert")
def reply_chat(farmer_id):
    if request.method == "POST":
        message = request.form.get("message")

        if message:
            db.session.add(
                ChatMessage(
                    sender="expert",
                    message=message,
                    farmer_id=farmer_id
                )
            )
            db.session.commit()

        return redirect(
            url_for("expert.reply_chat", farmer_id=farmer_id)
        )

    messages = (
        ChatMessage.query
        .filter_by(farmer_id=farmer_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return render_template(
        "expert/reply_chat.html",
        messages=messages,
        farmer_id=farmer_id
    )


# ===============================
# EXPERT CREATE DISEASE
# ===============================
@expert_bp.route("/diseases/create", methods=["GET", "POST"])
@role_required("expert")
def create_disease():
    crops = Crop.query.order_by(Crop.name.asc()).all()

    if request.method == "POST":
        crop_id = request.form.get("crop_id")
        name = request.form.get("name")
        description = request.form.get("description")
        severity = request.form.get("severity_level")

        if not crop_id or not name:
            flash("❌ Crop and disease name are required", "danger")
            return redirect(request.url)

        disease = Disease(
            crop_id=crop_id,
            name=name,
            description=description,
            severity_level=severity
        )

        db.session.add(disease)
        db.session.commit()

        flash("✅ Disease added successfully", "success")
        return redirect(url_for("expert.dashboard"))

    return render_template(
        "expert/create_disease.html",
        crops=crops
    )


# ===============================
# OPTIONAL FORM (FIXED ✅)
# ===============================
@expert_bp.route("/form", methods=["GET", "POST"])
@role_required("expert")
def form():
    if request.method == "POST":
        # Safe placeholder (prevents 405)
        flash("ℹ️ Form submitted successfully", "info")
        return redirect(url_for("expert.dashboard"))

    return render_template("expert/form.html")
