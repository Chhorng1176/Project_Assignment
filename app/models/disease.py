from app.extensions import db

class Disease(db.Model):
    __tablename__ = "diseases"

    id = db.Column(db.Integer, primary_key=True)

    crop_id = db.Column(
        db.Integer,
        db.ForeignKey("crops.id"),
        nullable=False
    )

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    severity_level = db.Column(db.String(50))

    crop = db.relationship(
        "Crop",
        back_populates="diseases"
    )

    def __repr__(self):
        return f"<Disease {self.name}>"
