from . import app, UPLOAD_FOLDER, db_manager

from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, url_for, request, redirect, send_from_directory

import os


def my_render_template(*args, **kwargs):
    return render_template(*args, **kwargs, login=current_user.is_authenticated)


# SMART PAGES
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/account', methods=['POST', 'GET'])
def account():
    if not current_user.is_authenticated:
        return redirect('/')
    db_manager.save_file(request)
    files = db_manager.get_files_for(current_user)
    return my_render_template('/account.html', files=files)


@app.route('/remove/' + UPLOAD_FOLDER + '/<string:user_login>' + '/<string:filename>')
@login_required
def remove(user_login: str, filename: str):
    if current_user.name == user_login:
        db_manager.remove_file(user_login, filename)
    return redirect('/account')


@app.route('/' + UPLOAD_FOLDER + '/<string:user_login>' + '/<string:filename>')
@login_required
def download(user_login: str, filename: str):
    if current_user.name == user_login:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user_login),
                                   filename, as_attachment=True)
    return 'Файл не найден :('


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
        print(request.form)
        username = request.form.get('Login')
        password = request.form.get('Password')
        user = db_manager.login_user(username, password)
        if user is not None:
            login_user(user)
            return redirect('/account')
        else:
            message = 'Неверный логин или пароль'
    return render_template('login.html', message=message)


@app.route('/support')
def support():
    return my_render_template('support.html')


@app.route('/')
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
