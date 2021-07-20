import os
import eventlet
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from whitenoise import WhiteNoise

eventlet.monkey_patch()

async_mode = 'eventlet'

csrf = CSRFProtect()
socketio = SocketIO()
login = LoginManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.DevelopmentConfig")
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    csrf.init_app(app)
    socketio.init_app(app, async_mode=async_mode, manage_session=False)
    login.init_app(app)
    login.login_view = 'main.login'
    db.init_app(app)
    with app.app_context():
        from app.main import main as main_blueprint
        from app.main import world
        app.register_blueprint(main_blueprint)
        WHITENOISE_MAX_AGE = 31536000 if not app.config["DEBUG"] else 0
        app.wsgi_app = WhiteNoise(
            app.wsgi_app,
            root=os.path.join(os.path.dirname(__file__), "staticfiles"),
            prefix="assets/",
            max_age=WHITENOISE_MAX_AGE,
        )
        world.clear_enemies(app=app)
        world.load_world()
        world.initiate_enemies(app=app)
    return app