from flask import Blueprint

main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static')

from app.main import routes, world

world.load_tiles()

