from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    report_name = db.Column(db.String(200))

    report_type = db.Column(db.String(100))

    health_score = db.Column(db.Integer)

    priority = db.Column(db.String(50))

    summary = db.Column(db.Text)

    analysis_json = db.Column(db.Text)

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )