from app import app, UPLOAD_FOLDER, login_manager
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, UserMixin
from werkzeug.utils import secure_filename
from datetime import datetime

import hashlib
import os


db_obj = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return db_obj.session.query(User).get(user_id)


def login_user(name, password):
    user = User.query.filter_by(name=name).first()
    if user is not None:
        key_from_db, salt = user.password, user.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        if key_from_db == key:
            return user
    return None


def get_friends_for_user(user):
    # need to add friends system
    return db_obj.session.query(User).all()


def add_new_user(name, password, email):
    user = User(name=name, password=b'', email=email, salt=b'')
    user.set_password(password)
    try:
        db_obj.session.add(user)
        db_obj.session.commit()
    except Exception as e:
        print('ERROR ADD REGISTERED USER TO DB')
        print(e.__class__.__name__)
        print(e)
        return False
    else:
        os.mkdir(os.path.join('app', 'static', 'files', user.name))
        return True


def save_file(file, desc):
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, current_user.name, filename)
    while os.path.isfile(path):
        path = add_numbered(path)
    os.system('pwd')
    file.save(os.path.join('app', path))
    if current_user.files:
        current_user.files += f'{path};'
    else:
        current_user.files = f'{path};'
    db_obj.session.add(File(name=filename, path=path, desc=desc))
    db_obj.session.commit()


class User(db_obj.Model, UserMixin):
    __tablename__ = 'users'
    id = db_obj.Column(db_obj.Integer, primary_key=True)
    name = db_obj.Column(db_obj.String(32), nullable=False)
    email = db_obj.Column(db_obj.String(32), nullable=False)
    salt = db_obj.Column(db_obj.LargeBinary(32), nullable=False)
    password = db_obj.Column(db_obj.LargeBinary(128), nullable=False)
    files = db_obj.Column(db_obj.Text)
    gives_files = db_obj.Column(db_obj.Text)

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


class File(db_obj.Model):
    # file_id = db.Column(db.Integer, primary_key=True)
    date = db_obj.Column(db_obj.DateTime, default=datetime.utcnow)
    name = db_obj.Column(db_obj.String(32), primary_key=True, nullable=False)
    desc = db_obj.Column(db_obj.Text, nullable=False)
    path = db_obj.Column(db_obj.String(32 + 32 + 16), nullable=False)


class Message(db_obj.Model):
    file_id = db_obj.Column(db_obj.Integer, primary_key=True)
    sent_date = db_obj.Column(db_obj.DateTime, default=datetime.utcnow)
    text = db_obj.Column(db_obj.Text, nullable=False)
    sender_id = db_obj.Column(db_obj.Integer, db_obj.ForeignKey('users.id'))
    receiver_id = db_obj.Column(db_obj.Integer, db_obj.ForeignKey('users.id'))


def get_messages_for_users(user1_id, user2_id):
    messages1 = db_obj.session.query(Message).filter(Message.sender_id == user1_id,
                                                    Message.receiver_id == user2_id)
    messages2 = db_obj.session.query(Message).filter(Message.sender_id == user2_id,
                                                    Message.receiver_id == user1_id)
    messages = []
    for i in messages1:
        messages.append(i)
    for i in messages2:
        messages.append(i)
    messages = sorted(messages, key=lambda m: m.sent_date)
    return messages



def remove_file(user_login, filename):
    path = os.path.join(user_login, filename)
    full_path = os.path.join('static', 'files', path)
    user = User.query.filter_by(name=user_login).one()
    if full_path not in user.files.split(';'):
        return
    File.query.filter_by(path=path).delete()
    db_obj.session.commit()
    files = user.files.split(';')
    print('files:', files)
    files.remove(full_path)
    user.files = ';'.join(files)
    db_obj.session.commit()
    try:
        os.remove(full_path)
    except FileNotFoundError:
        print(f'Файл {full_path} не существует')
    print('remove', full_path)
    print(user.files)


def get_files_for(user):
    if not user.files:
        return []

    class FileObj:
        def __init__(self, path: str, name: str, desc: str, date):
            self.path, self.name, self.desc = path, name, desc
            self.date = date
    files = []
    for file_path in user.files.split(';')[:-1]:
        name = os.path.split(file_path)[-1]
        f = File.query.get(name)
        files.append(FileObj(file_path, name, f.desc, f.date))
    return files


def name_in_db(name: str):
    return name.lower() in map(lambda x: x.name.lower(), User.query.filter_by(name=name).all())


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
