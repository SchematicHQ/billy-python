from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


######
# Model classes
######
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(250), unique=True, nullable=False)
    users = db.relationship("Users", backref="company", lazy=True, uselist=False)
    favorites = db.relationship("Favorites", backref="company", lazy=True)


class Favorites(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250), unique=True, nullable=False)
    photo_id = db.Column(db.String(250), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
