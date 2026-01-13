from flask import Flask

from .extensions import db, login_manager, migrate
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ===============================
    # INIT EXTENSIONS
    # ===============================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # 🔑 IMPORTANT: Flask-Migrate
    migrate.init_app(app, db)

    # ===============================
    # REGISTER BLUEPRINTS
    # ===============================
    from app.blueprints.main.routes import main_bp
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.expert.routes import expert_bp
    from app.blueprints.farmer.routes import farmer_bp
    from app.blueprints.user.routes import user_bp

    # Main & Auth
    app.register_blueprint(main_bp)     # /
    app.register_blueprint(auth_bp)     # /auth

    # Role-based Blueprints
    app.register_blueprint(admin_bp)    # /admin/...
    app.register_blueprint(expert_bp)   # /expert/...
    app.register_blueprint(farmer_bp)   # /farmer/...
    app.register_blueprint(user_bp)     # /user/...

    return app
