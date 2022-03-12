# url_for function is used by html pages
from flask import Flask, render_template, url_for, request, redirect, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy

from waitress import serve
from werkzeug.utils import secure_filename

import os
import hashlib



# Жалкие попытки подключить https
#from OpenSSL import SSL
# print(dir(SSL))
# context = SSL.Context(SSL.SSL3_VERSION)
# context.use_privatekey_file('hello')
# context.use_certificate_file('ssl/certificate.crt')


# CREATE
app = Flask(__name__)
login_manager = LoginManager(app)


# CONFIGURATE
TEST = False 
UPLOAD_FOLDER = 'static/files'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    #file_id = db.Column(db.Integer, primary_key=True)
    # date = db.Column(db.DateTime, nullable=False)  # Пока что не работает
    name = db.Column(db.String(32), primary_key=True, nullable=False)
    desc = db.Column(db.Text, nullable=False)
    path = db.Column(db.String(32+32+16), nullable=False)


# LOGIN
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


def my_render_template(*args, **kwargs):
    return render_template(*args, **kwargs, login=current_user.is_authenticated)


# SMART PAGES
@app.route('/account', methods=['POST', 'GET'])
def account():
    if current_user.is_anonymous:
        return redirect('/')
    if request.method == 'POST':
        desc = request.form["desc"]
        if request.files:
            try:
                save_file(request.files['File'], desc)
            except IsADirectoryError:
                pass
    files = get_files_for(current_user)
    return my_render_template('/account.html', files=files)


@app.route('/' + UPLOAD_FOLDER + '/<string:user_login>' + '/<string:filename>')
@login_required
def download(user_login: str, filename: str):
    if current_user.name == user_login:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user_login),
                                   filename, as_attachment=True)
    return 'Файл не найден :('


def remove_file(user_login, filename):
    path = os.path.join(user_login, filename)
    full_path = os.path.join('static', 'files', path)
    user = User.query.filter_by(name=user_login).one()
    if full_path not in user.files.split(';'):
        return
    File.query.filter_by(path=path).delete()
    db.session.commit()
    files = user.files.split(';')
    print('files:', files)
    files.remove(full_path)
    user.files = ';'.join(files)
    db.session.commit()
    try:
        os.remove(full_path)
    except FileNotFoundError:
        print(f'Файл {full_path} не существует')
    print('remove', full_path)
    print(user.files)


@app.route('/remove/' + UPLOAD_FOLDER + '/<string:user_login>' + '/<string:filename>')
@login_required
def remove(user_login: str, filename: str):
    if current_user.name == user_login:
        remove_file(user_login, filename)
    return redirect('/account')


def get_files_for(user):
    if not user.files:
        return []

    class FileObj:
        def __init__(self, path: str, name: str, desc: str):
            self.path, self.name, self.desc = path, name, desc
    files = []
    for file_path in user.files.split(';')[:-1]:
        name = os.path.split(file_path)[-1]
        print(File.query.get(name))
        files.append(FileObj(file_path, name, File.query.get(name).desc))
    return files


def check_incorrect_data(name: str, password: str, repeat_password: str) -> str:
    if len(name) < 4:
        return 'Логин должен состоять из более чем 4 символов'
    if len(name) > 32:
        return 'Максимальный размер логина - 32 символа'
    if not name.isalnum():
        return 'Имя не должно содержать спец.символов'
    if name_in_db(name):
        return 'Пользователь с таким логином уже существует'
    if len(password) < 4:
        return 'Пароль должен состоять из более чем 4 символов'
    if len(name) > 100:
        return 'Максимальный размер пароль - 100 символов'
    if password != repeat_password:
        return 'Пароли не совпадают'
    return ''


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/account')
    if request.method == 'POST':
        print(request.form)
        name = request.form['Login']
        email = request.form['Email']
        password = request.form['Password']
        repeat_password = request.form['RepeatPassword']
        message = check_incorrect_data(name, password, repeat_password)
        if message:
            return render_template('register.html', message=message)
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
    if current_user.is_authenticated:
        return redirect('/account')
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


def index_revert(path: str):
    for num, i in reversed(tuple(enumerate(path))):
        if i == '(':
            print(f'{num=}')
            return num


def is_numbered(path):
    return path.endswith(')') and '(' in path and path[index_revert(path) + 1:-1].isnumeric()


def add_numbered(path):
    number = 1
    ext = ''
    if '.' in path:
        ext = '.' + path.split('.')[-1]
        path = '.'.join(path.split('.')[:-1])
    if is_numbered(path):
        number = int(path[index_revert(path) + 1:-1]) + 1
        path = path[:index_revert(path)]
    return path + f'({number}){ext}'


def save_file(file, desc):
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.name, filename)
    while os.path.isfile(path):
        path = add_numbered(path)
    file.save(path)
    if current_user.files:
        current_user.files += f'{path};'
    else:
        current_user.files = f'{path};'
    db.session.add(File(name=filename, path=path, desc=desc))
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
    return render_template('login.html', message='Неверный логин или пароль')


def name_in_db(name: str):
    return name.lower() in map(lambda x: x.name.lower(), User.query.filter_by(name=name).all())


# PAGES
@app.route('/success_register')
def success_register():
    return my_render_template('success_register.html')


@app.route('/support')
def support():
    return my_render_template('support.html')


@app.route('/')
@app.route('/home')
def index():
    if current_user.is_authenticated:
        return redirect('/account')
    return render_template('index.html')


@app.route('/premium')
def premium():
    return my_render_template('premium.html')


@app.route('/about')
def about():
    return my_render_template('about.html')


@app.route('/politic')
def politic():
    return my_render_template('politic.html')


@app.route('/yandex_baf6d04d550034ad.html')
def yandex_check():
    return render_template('/yandex_baf6d04d550034ad.html')


if __name__ == "__main__":
    if TEST:
        app.run(debug=True, port=8080)
    else:
        serve(app, port=80)
