from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # 1. Load Configuration
    # (We will connect your config.py later, let's just get it running first)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

    # 2. Register Blueprints
    # This connects your routes to the app
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)

    @app.route('/')
    def home():
        return "<h1>Success! The Flask App is Running.</h1>"

    return app