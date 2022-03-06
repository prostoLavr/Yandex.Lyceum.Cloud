from flask import Flask

from flask_login import LoginManager

app = Flask(__name__)
login_manager = LoginManager(app)
UPLOAD_FOLDER = 'static/files'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../sqlite/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hello'


from app import views
