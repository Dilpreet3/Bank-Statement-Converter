from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='user')
    free_credits = db.Column(db.Integer, default=5)
    paid_credits = db.Column(db.Integer, default=0)
    unlimited_credits = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pdf_path = db.Column(db.String(200))
    excel_path = db.Column(db.String(200))
    status = db.Column(db.String(50), default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
