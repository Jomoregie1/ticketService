import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from app.models.userModel import User
from config import get_db_connection

# Load environment variables from .env file
load_dotenv()
mail = Mail()


def create_app():
    app = Flask(__name__)

    # Set secret key from environment variables
    app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')  # Default fallback

    # Add Flask-Mail Configuration
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")  # Default to Gmail
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False  # Set to True if using SSL instead of TLS
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # Your email
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")  # Your email password
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

    mail.init_app(app)  # ✅ Initialize Flask-Mail inside create_app()




    # Initialize Flask-Login
    login_manager = LoginManager(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM user WHERE id = %s"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            return User(
                id=user_data["id"],
                email=user_data["email"],
                password=user_data["password"],
                is_superuser=bool(user_data["is_superuser"])
            )

        return None

    # Blueprint imports
    from app.controllers.register_controller import signup
    from app.controllers.login_controller import login_bp
    from app.controllers.home_controller import home_blueprint
    from app.controllers.ticket_controller import ticket_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.ai_controller import ai_bp

    # Register blueprints
    app.register_blueprint(signup, url_prefix='/signup')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(home_blueprint, url_prefix='/home')
    app.register_blueprint(ticket_bp, url_prefix="/ticket")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(ai_bp, url_prefix="/estimate")

    @app.route("/")
    def default_route():
        return redirect("/login")

    return app
