from werkzeug.security import generate_password_hash
from app import db
from app.models.userModel import User


class UserService:
    @staticmethod
    def create_user(email, password):
        if User.query.filter_by(email=email).first():
            return {"error": "Email is already in use"}, 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User registered successfully!"}, 201

    @staticmethod
    def check_email_and_password(email, password):

        user = User.query.filter_by(email=email).first()

        if user:
            return {"error": "Email doesn't exist"}, 404

