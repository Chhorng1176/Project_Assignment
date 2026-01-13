from app.extensions import db


class Rule(db.Model):
    __tablename__ = "rules"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    solution = db.Column(db.Text)
    confidence = db.Column(db.Float)

    symptoms = db.relationship(
        "Symptom",
        secondary="rule_symptoms",
        back_populates="rules"
    )


class Symptom(db.Model):
    __tablename__ = "symptoms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    rules = db.relationship(
        "Rule",
        secondary="rule_symptoms",
        back_populates="symptoms"
    )


class RuleSymptom(db.Model):
    __tablename__ = "rule_symptoms"

    rule_id = db.Column(db.Integer, db.ForeignKey("rules.id"), primary_key=True)
    symptom_id = db.Column(db.Integer, db.ForeignKey("symptoms.id"), primary_key=True)
