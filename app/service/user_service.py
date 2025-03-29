from werkzeug.security import generate_password_hash, check_password_hash
from config import get_db_connection
from app.models.userModel import User, ks5_math_hash
from app.service.base_service import BaseService
from flask import current_app
import jwt
import datetime

#class for handling all user related operations
class UserService(BaseService):
    @staticmethod
    def create_user(email, password):              #creation of a user

        try:

            if User.find_by_email(email):          #if its in the DB already
                return {"error": "Email is already in use"}, 400


            # Creates the new user in DB
            User.create(email, password)
            return {"message": "User registered successfully!"}, 201

        except Exception as e:           #exception handling
            return {"error": f"An error occurred while creating the user: {e}"}, 500

    @staticmethod
    def check_email_and_password(email, password):   #checks if the credentials are corect

        try:

            user = User.find_by_email(email) #gets them by email

            # Verify the password
            if not user or not user.check_password(password):
                return None

            return user

        except Exception as e: #exception handling
            raise Exception(f"An error occurred while checking credentials: {e}")


    @staticmethod
    def delete_user(user_id):   #checks if they exist then it deletes them

        conn = BaseService.get_db_connection()
        cursor = conn.cursor()

        # Check if the user exists
        cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        #delete sthe user
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User deleted successfully!"}, 200

    @staticmethod
    def update_user(user_id, data):       #used when a user updates their password awell as if a admin changes the status of a user

        conn = BaseService.get_db_connection()  #inhertance
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM user WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"error": "User not found"}, 404

        email = data.get("email")         #extracts the update fields from data dictoinary
        password = data.get("password")
        is_superuser = data.get("is_superuser")

        update_fields = []
        update_values = []

        if email:                    #dynamic sql statements for updates
            update_fields.append("email = %s")
            update_values.append(email)

        if password:
            hashed_password = ks5_math_hash(password)
            update_fields.append("password = %s")
            update_values.append(hashed_password)

        if is_superuser is not None:
            update_fields.append("is_superuser = %s")
            update_values.append(bool(is_superuser))

        if not update_fields:
            return {"error": "No valid fields to update"}, 400

        update_values.append(user_id)                  #final sql statment with dynamic fields
        query = f"UPDATE user SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(update_values))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User updated successfully!"}, 200

    @staticmethod
    def get_all_users():         #gets all users for displayment on the admin table user page (normal users only)
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

    def get_user_by_id(user_id):       #selects all details from the user with a certain ID

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
                "is_superuser": user["is_superuser"],
            }
        return None

    #forgotten password stuff here. i have modelled it based off a friends version however i have made significant
    #changes in the way it operates and is used

    @staticmethod
    def generate_reset_token(email):                  #has been copied from online sources due to complexity
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        # Generates a secure JWT token for password reset
        # Token is valid for 1 hour
        payload = {"email": email, "exp": expiration}
        token = jwt.encode(payload, current_app.secret_key, algorithm="HS256")
        return token

    @staticmethod
    def verify_reset_token(token):         #has been copied from online sources due to complexity
        # Decodes and verifies the reset token
        try:
            payload = jwt.decode(token, current_app.secret_key, algorithms=["HS256"])
            return payload["email"]
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def update_password(email, new_password):          #updates the password with the new one the user inputs

        hashed_password = ks5_math_hash(new_password)        #uses the same hash method
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE user SET password = %s WHERE email = %s"
        cursor.execute(query, (hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Password updated successfully!"}, 200

    @staticmethod
    def get_user_by_email(email):      #gets the users details via email

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