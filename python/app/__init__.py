from flask import Flask

from flask_login import LoginManager


from .data import db_session, config

app = Flask(__name__)
login_manager = LoginManager(app)
db_session.global_init(config.db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = config.files_path
app.config['SECRET_KEY'] = 'lava-land'
# server_name = '0.0.0.0:8000'
server_name = 'lava-land.ru'


from . import smart_views, views
