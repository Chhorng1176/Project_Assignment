from flask import Blueprint
from .routes import expert_bp

expert_bp = Blueprint(
    "expert",
    __name__,
    template_folder="../../templates/expert"
)

from . import routes
