import hashlib
import os
from waitress import serve
from werkzeug.utils import secure_filename

# url_for function is used by html pages
from flask import Flask, render_template, url_for, request, redirect, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
import os
import hashlib


# CREATE
app = Flask(__name__)
login_manager = LoginManager(app)


# CONFIGURATE
TEST = True
UPLOAD_FOLDER = 'static/files'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'hello'


# DATABASE
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)
    salt = db.Column(db.LargeBinary(32), nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    files = db.Column(db.Text)
    gives_files = db.Column(db.Text)

    def check_password(self, password):
        key_from_db, salt = self.password, self.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        return key_from_db == key

    def set_password(self, password):
        salt = os.urandom(32)
        self.salt = salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        self.password = key

    def __repr__(self):
        return f'<User {self.id}>'


class File(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    path = db.Column(db.String(64), nullable=False)


# LOGIN
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')

# SMART PAGES
@app.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    if request.method == 'POST':
        if request.files:
            save_file(request.files['File'])

    files = get_files_for(current_user)
    return render_template('/account.html', files=files)


@app.route('/' + UPLOAD_FOLDER + '/<string:user_login>' + '/<string:filename>')
@login_required
def download(user_login: str, filename: str):
    if current_user.name == user_login:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user_login),
                                   filename, as_attachment=True)
    return 'Файл не найден :('


def get_files_for(user):
    if not user.files:
        return []

    class FileObj:
        def __init__(self, path: str, name: str):
            self.path, self.name = path, name
    files = []
    for file_path in user.files.split(';')[:-1]:
        files.append(FileObj(file_path, os.path.split(file_path)[-1]))
    return files


def is_incorrect_data(name, password):
    return (name_in_db(name) or len(name) < 4 or not name.isidentifier()
            or len(password) < 4 or len(name) > 32 or len(password) > 128)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        name = request.form['Login']
        email = request.form['Email']
        password = request.form['Password']
        repeat_password = request.form['RepeatPassword']

        if is_incorrect_data(name, password) or password != repeat_password:
            return redirect('/register')
        return add_new_user(name, password, email)
    else:
        return render_template('register.html')


def add_new_user(name, password, email):
    user = User(name=name, password=b'', email=email, salt=b'')
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print('ERROR ADD REGISTERED USER TO DB')
        print(e.__class__.__name__)
        print(e)
        return "Не удалось добавить аккаунт! Повторите попытку позже :("
    else:
        os.mkdir(os.path.join('static', 'files', user.name))
        return redirect('/success_register')


@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('Login')
        password = request.form.get('Password')
        user = db.session.query(User).filter(User.name == username).first()
        print('found user', user)
        if user and user.check_password(password):
            login_user(user)
            return redirect('/account')
        else:
            message = 'Неверный логин или пароль'
    return render_template('login.html', message=message)


def save_file(file):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.name, filename)
    file.save(path)
    if current_user.files:
        current_user.files += f'{path};'
    else:
        current_user.files = f'{path};'
    print(current_user.files)
    db.session.add(File(name=filename, path=path))
    db.session.commit()


def confirm_login(name, password):
    print(f'{name=}, {password=}')
    user = User.query.first()
    if user is not None:
        key_from_db, salt = user.password, user.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        if key_from_db == key:
            files = File.query.all()
            return render_template('account.html', files=files)
    return render_template('login_error.html')


def name_in_db(name: str):
    print(name, 'in', User.query.filter_by(name=name).all())
    return name in map(lambda x: x.name, User.query.filter_by(name=name).all())


# PAGES
@app.route('/incorrect_password')
def incorrect_password():
    return render_template('login_error.html')


@app.route('/success_register')
def success_register():
    return render_template('success_register.html')


@app.route('/support')
def support():
    return render_template('support.html')


@app.route('/')
@app.route('/home')
def index():
    print(current_user.is_authenticated)
    if current_user.is_authenticated:
        return redirect('/account')
    return render_template('index.html')


if __name__ == "__main__":
    if TEST:
        app.run(debug=True, port=8080)
    else:
        serve(app, port=8080)
