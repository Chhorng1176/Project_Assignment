# seed_expert.py
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    if User.query.filter_by(username="expert1").first():
        print("⚠️ Expert already exists")
        exit()

    expert = User(
        username="expert1",
        password_hash=generate_password_hash("expert123")
    )

    expert_role = Role.query.filter_by(name="expert").first()
    if not expert_role:
        print("❌ Expert role not found")
        exit()

    expert.roles.append(expert_role)
    db.session.add(expert)
    db.session.commit()

    print("✅ Expert user created (expert1 / expert123)")
