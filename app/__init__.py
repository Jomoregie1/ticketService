from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models.userModel import User
from config import Config

db = SQLAlchemy()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manger = LoginManager(app)

    with app.app_context():
        db.create_all()

    @login_manger.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

    from app.controllers.register_controller import signup
    from app.controllers.login_controller import login
    app.register_blueprint(signup, url_prefix='/signup')
    app.register_blueprint(login, url_prefix='/login')

    return app
