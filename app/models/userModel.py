from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from config import get_db_connection
import hashlib

PRIME = 104729

def ks5_math_hash(password: str) -> str:
    #a normal hashing method to ensure complexity whilst using advance ks5 maths for extra marks + security
    numeric_value = sum(ord(char) ** 2 for char in password) % PRIME
    hashed_value = hashlib.sha256(str(numeric_value).encode()).hexdigest()
    print(f"🔍 KS5 Hashing - Input: {password}, Numeric: {numeric_value}, Hash: {hashed_value}")  #  Debugging
    return hashed_value

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

        hashed_password = ks5_math_hash(password)
        print(f" Storing hashed password: {hashed_password}") # Debugging stuff
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO user (email, password) VALUES (%s, %s)"
        cursor.execute(query, (email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def find_by_email(email):              #gets all details of a user with set email

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
    def find_by_id(user_id):                      #gets users details by the ID matched from a ticket

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

        hashed_attempt = ks5_math_hash(password)
        print(f"🔍 Expected Hash (DB): {self.password}")  # Debugging
        print(f"🔍 Attempted Hash (Input): {hashed_attempt}")  # Debugging
        return hashed_attempt == self.password
