import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate

from config import get_db_connection

# Load environment variables from .env file
load_dotenv()


def create_app():
    app = Flask(__name__)

    # Set secret key from environment variables
    app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')  # Default fallback

    # Initialize Flask-Login
    login_manager = LoginManager(app)

    # User loader for Flask-Login using raw SQL
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            return {
                "id": user["id"],
                "email": user["email"],
                "password": user["password"]
            }
        return None

    # Blueprint imports
    from app.controllers.register_controller import signup
    from app.controllers.login_controller import login_bp
    from app.controllers.home_controller import home_blueprint

    # Register blueprints
    app.register_blueprint(signup, url_prefix='/signup')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(home_blueprint, url_prefix='/home')

    return app
