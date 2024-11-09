from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.models.userModel import User, db
from config import Config


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
    from app.controllers.login_controller import login_bp
    from app.controllers.home_controller import home_blueprint
    app.register_blueprint(signup, url_prefix='/signup')
    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(home_blueprint, url_prefix='/home')

    return app
