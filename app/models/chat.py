from datetime import datetime
from app.extensions import db

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)

    sender = db.Column(
        db.String(20),
        nullable=False
    )  # farmer | system | expert

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Chat {self.sender}: {self.message[:20]}>"
