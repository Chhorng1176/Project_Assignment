from flask import Blueprint, render_template

user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/users"
)


@user_bp.route("/")
def index():
    return render_template("users/index.html")
