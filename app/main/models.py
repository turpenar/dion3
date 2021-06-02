from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

class User(UserMixin, db.Model):
    """"""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    character_1 = db.Column(db.PickleType)
    character_2 = db.Column(db.PickleType)
    character_3 = db.Column(db.PickleType)
    character_4 = db.Column(db.PickleType)
    character_5 = db.Column(db.PickleType)
    
    def __init__(self, username):
        self.username = username
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
        