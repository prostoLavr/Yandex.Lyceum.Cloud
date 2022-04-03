from . import app
from .data import db_manager
from .data.db_manager import my_render_template

from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, request, redirect


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/account')
def account():
    if not current_user.is_authenticated:
        return redirect('/')
    files = db_manager.get_files_for(current_user)
    return my_render_template('/account.html', files=files)


@app.route('/load', methods=['GET', 'POST'])
def load():
    if request.method == 'POST':
        db_manager.save_file(request)
        return redirect('/account')
    return my_render_template('load.html')


@app.route('/remove/<string:file_id>')
@login_required
def remove(file_id):
    db_manager.remove_file(current_user, file_id)
    return redirect('/account')


@app.route('/download/<string:file_id>')
@login_required
def download(file_id):
    res = db_manager.download_file(current_user, file_id)
    if res is None:
        return 'Файл не найден :('
    return res


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/account')
    if request.method == 'POST':
        error_message = db_manager.add_new_user(request.form)
        if error_message:
            return render_template('register.html', message=error_message)
        else:
            return my_render_template('success_register.html')
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ''
    if current_user.is_authenticated:
        return redirect('/account')
    if request.method == 'POST':
        username = request.form.get('Login')
        password = request.form.get('Password')
        user = db_manager.login_user(username, password)
        if user is not None:
            login_user(user)
            return redirect('/account')
        else:
            message = 'Неверный логин или пароль'
    return render_template('login.html', message=message)


@app.route('/messenger')
def messenger():
    if current_user.is_anonymous:
        return redirect('/')
    user_friends = db_manager.get_friends_for_user(current_user.id)
    return my_render_template('messenger.html', users=user_friends)


@app.route('/messenger/<user_id>', methods=['POST', 'GET'])
@login_required
def chat(user_id):
    if request.method == 'POST':
        message = request.form['message']
        db_manager.add_message(message, user_id, current_user.id)
    messages = db_manager.get_messages_for_users(current_user.id, user_id)
    user_friend = db_manager.load_user(user_id)
    return my_render_template('chat.html', messages=messages, friend=user_friend)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/account')
    return render_template('index.html')
