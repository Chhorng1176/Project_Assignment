from app.extensions import db

class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    disease_id = db.Column(
        db.Integer,
        db.ForeignKey("diseases.id"),
        nullable=False
    )

    # simple rule: comma-separated symptoms
    symptoms = db.Column(db.Text, nullable=False)

    confidence = db.Column(db.Float, default=0.0)

    disease = db.relationship("Disease", backref="rules")

    def symptom_list(self):
        return [s.strip().lower() for s in self.symptoms.split(",")]

    def __repr__(self):
        return f"<Rule {self.name}>"
