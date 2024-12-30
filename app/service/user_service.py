from werkzeug.security import generate_password_hash, check_password_hash
from app.models.userModel import User


class UserService:
    @staticmethod
    def create_user(email, password):
        """
        Create a new user if the email is not already in use.
        """
        try:
            # Check if the email is already in use
            if User.find_by_email(email):
                return {"error": "Email is already in use"}, 400

            # Create the new user
            User.create(email, password)
            return {"message": "User registered successfully!"}, 201

        except Exception as e:
            return {"error": f"An error occurred while creating the user: {e}"}, 500

    @staticmethod
    def check_email_and_password(email, password):
        """
        Check the provided email and password and return the user if valid.
        """
        try:
            # Retrieve the user by email
            user = User.find_by_email(email)

            # Verify the password
            if not user or not user.check_password(password):
                return None

            return user

        except Exception as e:
            raise Exception(f"An error occurred while checking credentials: {e}")