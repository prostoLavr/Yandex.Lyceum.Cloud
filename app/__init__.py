from flask import Flask
from flask_login import LoginManager

import os

from .data import db_session, config


wsgi_app = Flask(__name__)
login_manager = LoginManager(wsgi_app)
db_session.global_init(config.db_path)
wsgi_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.db_path}'
wsgi_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
wsgi_app.config['MAX_CONTENT_LENGTH'] = 17179869184
wsgi_app.config['UPLOAD_FOLDER'] = config.files_path
wsgi_app.config['SECRET_KEY'] = os.urandom(24)
server_name = 'lava-land.ru'


from . import smart_views, views, error_views
