import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:123@localhost:5432/AssExpertsystem"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
