from . import db
from sqlalchemy import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    is_github_account = db.Column(db.Boolean, default=False)
    confirmed_email = db.Column(db.Boolean, default=False)
    confirm_code = db.Column(db.String(65))

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(100))
    IATACode = db.Column(db.String(3))
    departure_city = db.Column(db.String(100))
    arrival_city = db.Column(db.String(100))