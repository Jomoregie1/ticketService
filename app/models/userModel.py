from werkzeug.security import generate_password_hash

from app import db


class User(db.Model):
    __tablename__ = 'user'
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))

    def __init__(self, email, password):
        self.email = email
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def __repr__(self):
        return f"User('{self.email}')"
