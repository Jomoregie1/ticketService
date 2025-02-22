from werkzeug.security import generate_password_hash, check_password_hash
from app.models.userModel import User
from config import get_db_connection


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


    @staticmethod
    def delete_user(user_id):
        """Delete a user from the database."""
        conn = get_db_connection()
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
        """Update user information (email or password)."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure the user exists before updating
        cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        # Update email and/or password if provided
        email = data.get("email")
        password = data.get("password")
        update_fields = []
        update_values = []

        if email:
            update_fields.append("email = %s")
            update_values.append(email)

        if password:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            update_fields.append("password = %s")
            update_values.append(hashed_password)

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
            conn = get_db_connection()
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
        conn = get_db_connection()
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