# app/blueprints/farmer/routes.py

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import current_user

from app.utils.decorators import farmer_required
from app.extensions import db

from app.models.crop import Crop
from app.models.diagnosis import Diagnosis
from app.models.chat_message import ChatMessage
from app.services.rule_engine import diagnose as rule_diagnose


# ===============================
# FARMER BLUEPRINT
# ===============================
farmer_bp = Blueprint(
    "farmer",
    __name__,
    url_prefix="/farmer"
)


# ===============================
# FARMER DASHBOARD
# ===============================
@farmer_bp.route("/dashboard")
@farmer_required
def dashboard():
    """
    Show diagnoses submitted by this farmer only
    """

    diagnoses = (
        Diagnosis.query
        .filter_by(farmer_id=current_user.id)
        .order_by(Diagnosis.created_at.desc())
        .all()
    )

    return render_template(
        "farmer/dashboard.html",
        diagnoses=diagnoses
    )


# ===============================
# FARMER AUTO DIAGNOSIS (STEP 11+)
# ===============================
@farmer_bp.route("/diagnose", methods=["GET", "POST"])
@farmer_required
def diagnose():
    """
    Farmer submits crop + symptoms
    System uses Rule Engine to auto-diagnose
    """

    crops = Crop.query.order_by(Crop.name.asc()).all()

    # Sidebar: recent diagnoses
    diagnoses = (
        Diagnosis.query
        .filter_by(farmer_id=current_user.id)
        .order_by(Diagnosis.created_at.desc())
        .limit(10)
        .all()
    )

    if request.method == "POST":
        crop_id = request.form.get("crop_id")
        symptoms_text = request.form.get("symptoms")

        if not crop_id or not symptoms_text:
            flash("❌ Please select crop and enter symptoms", "danger")
            return redirect(request.url)

        crop = Crop.query.get(crop_id)
        if not crop:
            flash("❌ Invalid crop selected", "danger")
            return redirect(request.url)

        # ---------------------------------
        # RULE ENGINE
        # ---------------------------------
        symptoms_list = [
            s.strip().lower()
            for s in symptoms_text.split(",")
            if s.strip()
        ]

        result = rule_diagnose(symptoms_list)

        if result:
            rule = result["rule"]
            matched_symptoms = result["matched_symptoms"]

            disease_name = rule.disease.name if rule.disease else "Unknown"
            confidence = rule.confidence
        else:
            disease_name = "Unknown"
            confidence = None
            matched_symptoms = []

        diagnosis = Diagnosis(
            farmer_id=current_user.id,
            crop_name=crop.name,
            disease_name=disease_name,
            symptoms=symptoms_text,
            status="AUTO",
            confidence=confidence
        )

        db.session.add(diagnosis)
        db.session.commit()

        flash("✅ Diagnosis completed successfully", "success")

        return redirect(
            url_for(
                "farmer.diagnosis_result",
                diagnosis_id=diagnosis.id
            )
        )

    return render_template(
        "farmer/diagnose.html",
        crops=crops,
        diagnoses=diagnoses
    )


# ===============================
# DIAGNOSIS RESULT
# ===============================
@farmer_bp.route("/result/<int:diagnosis_id>")
@farmer_required
def diagnosis_result(diagnosis_id):
    """
    Show diagnosis result (owner only)
    """

    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)

    # Security: owner only
    if diagnosis.farmer_id != current_user.id:
        flash("❌ Access denied", "danger")
        return redirect(url_for("farmer.dashboard"))

    # Sidebar: recent diagnoses
    diagnoses = (
        Diagnosis.query
        .filter_by(farmer_id=current_user.id)
        .order_by(Diagnosis.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "farmer/result.html",
        diagnosis=diagnosis,
        diagnoses=diagnoses
    )


# ===============================
# FARMER CHAT (ChatGPT STYLE)
# ===============================
@farmer_bp.route("/chat", methods=["GET", "POST"])
@farmer_required
def chat():
    """
    Farmer chat page (ChatGPT-style UI)
    """

    # Sidebar: recent diagnoses
    diagnoses = (
        Diagnosis.query
        .filter_by(farmer_id=current_user.id)
        .order_by(Diagnosis.created_at.desc())
        .limit(10)
        .all()
    )

    # ---------------------------------
    # POST → Save message
    # ---------------------------------
    if request.method == "POST":
        user_message = request.form.get("message")

        if user_message:
            db.session.add(
                ChatMessage(
                    sender="farmer",
                    message=user_message,
                    farmer_id=current_user.id
                )
            )

            # 🔜 STEP 14: AI auto-reply here
            db.session.add(
                ChatMessage(
                    sender="system",
                    message="🌱 Thanks for your question. Our AI expert is analyzing it.",
                    farmer_id=current_user.id
                )
            )

            db.session.commit()

        return redirect(url_for("farmer.chat"))

    # ---------------------------------
    # GET → Load messages
    # ---------------------------------
    messages = (
        ChatMessage.query
        .filter_by(farmer_id=current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return render_template(
        "farmer/chat.html",
        messages=messages,
        diagnoses=diagnoses
    )
