from werkzeug.security import generate_password_hash, check_password_hash
from config import get_db_connection
from app.models.userModel import User, ks5_math_hash
from app.service.base_service import BaseService
from flask import current_app
import jwt
import datetime


class UserService(BaseService):
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


    @staticmethod
    def delete_user(user_id):
        """Delete a user from the database."""
        conn = BaseService.get_db_connection()  #inheritance
        cursor = conn.cursor()

        # Ensure the user exists before deletion
        cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        # Delete user
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User deleted successfully!"}, 200

    @staticmethod
    def update_user(user_id, data):
        """Update user information (email, password, or superuser status)."""
        conn = BaseService.get_db_connection()  #inheritance
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        email = data.get("email")
        password = data.get("password")
        is_superuser = data.get("is_superuser")

        update_fields = []
        update_values = []

        if email:
            update_fields.append("email = %s")
            update_values.append(email)

        if password:
            hashed_password = ks5_math_hash(password)  # ✅ Use KS5 Hashing
            update_fields.append("password = %s")
            update_values.append(hashed_password)

        if is_superuser is not None:
            update_fields.append("is_superuser = %s")
            update_values.append(bool(is_superuser))

        if not update_fields:
            return {"error": "No valid fields to update"}, 400

        update_values.append(user_id)
        query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(update_values))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User updated successfully!"}, 200

    @staticmethod
    def get_all_users():
        try:
            conn = BaseService.get_db_connection()  #inheritance
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM user WHERE is_superuser = FALSE"
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            return {"error": str(e)}, 500

    def get_user_by_id(user_id):
        """Retrieve a user by their ID."""
        conn = BaseService.get_db_connection()  #inheritance
        cursor = conn.cursor(dictionary=True)

        query = "SELECT id, email, password, is_superuser FROM user WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "password": user["password"],
                "is_superuser": user["is_superuser"],  # ✅ Include superuser status
            }
        return None

    #forgotten password stuff here

    @staticmethod
    def generate_reset_token(email):
        """Generate a secure JWT reset token for password recovery."""
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token valid for 1 hour
        payload = {"email": email, "exp": expiration}
        token = jwt.encode(payload, current_app.secret_key, algorithm="HS256")
        return token

    @staticmethod
    def verify_reset_token(token):
        """Verify the password reset token."""
        try:
            payload = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
            return payload["email"]
        except jwt.ExpiredSignatureError:
            return None  # Token expired
        except jwt.InvalidTokenError:
            return None  # Invalid token

    @staticmethod
    def update_password(email, new_password):
        """Update the user’s password with a securely hashed version."""
        hashed_password = ks5_math_hash(new_password)  # Use KS5 hashing
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE user SET password = %s WHERE email = %s"
        cursor.execute(query, (hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Password updated successfully!"}, 200

    @staticmethod
    def get_user_by_email(email):
        """Retrieve a user by their email address."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "password": user["password"],
                "is_superuser": bool(user["is_superuser"])
            }
        return None