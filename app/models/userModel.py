from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from config import get_db_connection


class User(UserMixin):
    def __init__(self, id, email, password, is_superuser=False):
        self.id = id
        self.email = email
        self.password = password
        self.is_superuser = bool(is_superuser)

    def __repr__(self):
        return f"User('{self.email}')"

    def is_authenticated(self):
        return True

    @staticmethod
    def create(email, password):
        """Create a new user and store it in the database."""
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO user (email, password) VALUES (%s, %s)"
        cursor.execute(query, (email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def find_by_email(email):
        """Retrieve a user by their email."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return User(result['id'], result['email'], result['password'], bool(result['is_superuser']))
        return None

    @staticmethod
    def find_by_id(user_id):
        """Retrieve a user by their ID."""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            return User(result['id'], result['email'], result['password'], bool(result['is_superuser']))
        return None

    def check_password(self, password):
        """Verify the password."""
        return check_password_hash(self.password, password)
