import datetime

from . import UPLOAD_FOLDER, login_manager, db_session
from flask_login import current_user
from werkzeug.utils import secure_filename
from .data.users import User
from .data.files import File

import hashlib
import os
import uuid


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

    user = User(name=name, password=b'', email=email, salt=b'').with_password(password)
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
    if request.method != 'POST':
        return
    file = request.files['File']
    desc = request.form["desc"]

    path = UPLOAD_FOLDER
    while os.path.exists(path):
        path = os.path.join(UPLOAD_FOLDER, uuid.uuid4().hex)

    filename = secure_filename(file.filename)
    while os.path.isfile(filename):
        filename = add_numbered(filename)

    file.save(path)
    file = File(name=filename, path=path, desc=desc, date=datetime.date.today())
    print(file)
    db_sess = db_session.create_session()
    current_user.add_file(file.id)
    db_sess.add(file)
    db_sess.commit()


def remove_file(user, file_id):
    if file_id not in user.get_files():
        return
    db_sess = db_session.create_session()
    file = db_sess.query(File).filter_by(id=file_id).first()
    try:
        os.remove(file.path)
    except FileNotFoundError:
        print(f'Файл {file.path} не существует')
    db_sess.delete(file)
    user.remove_file(file.id)
    db_sess.commit()


def get_files_for(user):
    if not user.files:
        return []
    db_sess = db_session.create_session()
    files = []
    print('files:', user.get_files())
    for file_id in user.get_files():
        file = db_sess.query(File).filter_by(id=file_id).first()
        if file is not None:
            files.append(file)
    return files


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
