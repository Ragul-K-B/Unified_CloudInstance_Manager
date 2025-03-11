from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):  # Add UserMixin here

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # AWS Credentials
    access = db.Column(db.String(100))
    secret = db.Column(db.String(100))

    # Azure Credentials
    client_id = db.Column(db.String(100))
    tenant_id = db.Column(db.String(100))
    client_secret = db.Column(db.String(100))
    subscription_id = db.Column(db.String(100))
