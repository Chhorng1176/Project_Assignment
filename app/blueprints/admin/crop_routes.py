from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.utils.decorators import permission_required
from app.extensions import db
from app.models.crop import Crop

admin_crop_bp = Blueprint(
    "admin_crop",
    __name__,
    url_prefix="/admin/crops"
)


@admin_crop_bp.route("/")
@login_required
@permission_required("manage_crops")
def index():
    crops = Crop.query.all()
    return render_template("admin/crops/index.html", crops=crops)


@admin_crop_bp.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("manage_crops")
def create():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")

        if not name:
            flash("❌ Crop name is required", "danger")
            return redirect(request.url)

        crop = Crop(name=name, description=description)
        db.session.add(crop)
        db.session.commit()

        flash("✅ Crop added successfully", "success")
        return redirect(url_for("admin_crop.index"))

    return render_template("admin/crops/create.html")


@admin_crop_bp.route("/<int:id>/delete")
@login_required
@permission_required("manage_crops")
def delete(id):
    crop = Crop.query.get_or_404(id)
    db.session.delete(crop)
    db.session.commit()

    flash("🗑 Crop deleted", "warning")
    return redirect(url_for("admin_crop.index"))
