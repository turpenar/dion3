import eventlet
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

eventlet.monkey_patch()

async_mode = 'eventlet'
debug = True

csrf = CSRFProtect()
socketio = SocketIO()
login = LoginManager()
db = SQLAlchemy()

def create_app(debug=debug):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Your Kung-Fu is Very Good'
    app.config['DEBUG'] = debug
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main/users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_TYPE'] = "sqlalchemy"
    app.config['SESSION_SQLALCHEMY'] = db
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    csrf.init_app(app)
    socketio.init_app(app, async_mode=async_mode, manage_session=False)
    login.init_app(app)
    login.login_view = 'main.login'
    db.init_app(app)
    with app.app_context():
        from app.main import main as main_blueprint
        app.register_blueprint(main_blueprint)
        return app