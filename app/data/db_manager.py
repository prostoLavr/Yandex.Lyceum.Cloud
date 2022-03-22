from app import login_manager, db_session
from flask_login import current_user
from flask import send_file
from werkzeug.utils import secure_filename
import transliterate

from .users import User
from .files import File
from .messages import Message
from . import config

import hashlib
import os
import uuid
import datetime


def get_friends_for_user(user):
    # need to add friends system
    db_sess = db_session.create_session()
    return db_sess.query(User).all()


def get_messages_for_users(user1_id, user2_id):
    db_sess = db_session.create_session()
    messages1 = db_sess.query(Message).filter_by(sender_id=user1_id, receiver_id=user2_id).all()
    messages2 = db_sess.query(Message).filter_by(sender_id=user2_id, receiver_id=user1_id).all()
    messages = messages1 + messages2
    messages = sorted(messages, key=lambda m: m.sent_date)
    return messages


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def login_user(name, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter_by(name=name).first()
    if user is not None:
        key_from_db, salt = user.password, user.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        if key_from_db == key:
            return user
    return None


def add_new_user(form: dict) -> str:
    name = form['Login']
    email = form['Email']
    password = form['Password']
    repeat_password = form['RepeatPassword']

    error_message = check_incorrect_data(name, password, repeat_password)
    if error_message:
        return error_message

    user = User().with_password(password)
    user.name, user.email = name, email
    try:
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
    except Exception as e:
        print('ERROR ADD REGISTERED USER TO DB')
        print(e.__class__.__name__)
        print(e)
        return 'Не удалось создать аккаунт. Повторите попытку позднее'
    return ''


def save_file(request):
    file = request.files['File']
    desc = request.form["desc"]

    path = uuid.uuid4().hex
    while os.path.exists(path):
        path = uuid.uuid4().hex

    filename = file.filename
    if transliterate.detect_language(filename):
        filename = transliterate.translit(filename, reversed=True)
    filename = secure_filename(filename)

    file.save(os.path.join(config.files_path, path))
    file = File(name=filename, path=path, desc=desc, date=datetime.date.today())
    db_sess = db_session.create_session()
    db_sess.add(file)
    user = db_sess.query(User).filter_by(id=current_user.id).first()
    user.add_file(file.id)
    db_sess.commit()


def remove_file(user, file_path):
    db_sess = db_session.create_session()
    print(file_path)
    file = db_sess.query(File).filter_by(path=file_path).first()
    if file.id not in user.get_files():
        return
    try:
        os.remove(os.path.join(config.files_path, file.path))
    except FileNotFoundError:
        print(f'Файл {file.path} не существует')
    db_sess.delete(file)
    user.remove_file(file.id)
    db_sess.commit()


def download_file(user, file_path):
    db_sess = db_session.create_session()
    file = db_sess.query(File).filter_by(path=file_path).first()
    if not (file.id in user.get_files() + user.get_given_files()):
        return ''
    full_file_path = os.path.join(config.shorts_files_path, file.path)
    print('download', full_file_path)
    return send_file(full_file_path, download_name=file.name, as_attachment=True)


def get_files_for(user):
    if not user.files:
        return []
    db_sess = db_session.create_session()
    print('user have', db_sess.query(File).filter(File.id.in_(user.get_files())).all())
    return db_sess.query(File).filter(File.id.in_(user.get_files())).all()


def name_in_db(name: str):
    db_sess = db_session.create_session()
    return name.lower() in map(lambda x: x.name.lower(), db_sess.query(User).all())


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
        return 'Максимальный размер пароля - 100 символов'
    if password != repeat_password:
        return 'Пароли не совпадают'
    return ''


def index_revert(path: str):
    for num, i in reversed(tuple(enumerate(path))):
        if i == '(':
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
