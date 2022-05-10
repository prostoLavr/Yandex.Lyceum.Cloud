from flask import Flask
from flask_login import LoginManager

import os

from .data import db_session, config


app = Flask(__name__)
login_manager = LoginManager(app)
db_session.global_init(config.db_path)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 17179869184
app.config['UPLOAD_FOLDER'] = config.files_path
app.config['SECRET_KEY'] = os.urandom(24)
server_name = 'lava-land.ru'


from . import smart_views, views, error_views
