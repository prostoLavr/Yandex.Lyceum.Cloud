from flask_login import login_required, login_user, current_user, logout_user
from flask import request, redirect

from . import wsgi_app, server_name
from .data import db_manager
from .data.db_manager import my_render_template
from .data.exceptions import IncorrectData


@wsgi_app.route('/account/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


@wsgi_app.route('/cloud')
def cloud():
    if current_user.is_anonymous:
        return redirect('/login?page=/cloud')
    files = db_manager.get_files_for(current_user)
    return my_render_template('cloud.html', files=files)


@wsgi_app.route('/cloud/load', methods=['GET', 'POST'])
def load():
    if current_user.is_anonymous:
        return redirect('/')
    if request.method == 'POST':
        path_to_file = db_manager.save_file(request)
        return redirect(f'/cloud/edit_file/{path_to_file}')
    return my_render_template('load.html', active_page='cloud')


@wsgi_app.route('/cloud/load/success')
def success_load():
    return redirect('/cloud')


@login_required
@wsgi_app.route('/cloud/remove/<string:file_path>')
def remove(file_path):
    db_manager.remove_file(current_user, file_path)
    return redirect('/cloud')


@wsgi_app.route('/cloud/download/<string:file_path>')
def download(file_path):
    res = db_manager.download_file(current_user, file_path)
    if res is None:
        return redirect('/file_not_found')
    return res


@wsgi_app.route('/account/register', methods=['POST', 'GET'])
def register():
    active_page = request.args.get('page')
    if active_page is None:
        active_page = '/index'
    if current_user.is_authenticated:
        return redirect(active_page)
    if request.method == 'GET':
        return my_render_template('register.html', active_page=active_page)

    username = request.form.get('Login')
    password = request.form.get('Password')
    try:
        db_manager.add_new_user(request.form)
        user = db_manager.login_user_by_password(username, password)
        login_user(user)
    except IncorrectData as e:
        return my_render_template('register.html', message=e, **request.form,
                                  active_page=active_page)
    except Exception as e:
        # TODO: logs
        print('ERROR')
        print(e.__name__, e, '\n')
        return my_render_template('register.html',
                                  message='Что-то пошло не так. Повторите попытку позже.',
                                  active_page=active_page,
                                  **request.form)
    return redirect('/cloud')


@wsgi_app.route('/', methods=['POST', 'GET'])
@wsgi_app.route('/index', methods=['POST', 'GET'])
def index():
    return my_render_template('about.html', active_page='/index')


@wsgi_app.route('/login', methods=['POST', 'GET'])
def login():
    active_page = request.args.get('page')
    if active_page is None:
        active_page = '/cloud'
    if current_user.is_authenticated:
        return redirect(active_page)
    if request.method == 'POST':
        try:
            username = request.form.get('Login')
            password = request.form.get('Password')
            remember_me = request.form.get('RememberMe')
            user = db_manager.login_user_by_password(username, password)
            login_user(user, remember=bool(remember_me))
        except IncorrectData as e:
            return my_render_template('login.html', message=e,
                                      form=request.form,
                                      active_page=active_page)
        except Exception as e:
            # TODO: logs
            print('ERROR')
            print(e.__name__, e, '\n')
            return my_render_template('login.html',
                                      message='Что-то пошло не так. Повторите попытку позже.',
                                      form=request.form,
                                      active_page=active_page)
        else:
            return redirect(active_page)
    return my_render_template('login.html', active_page=active_page)


@wsgi_app.route('/messenger/accept_req/<string:user_id>')
@login_required
def accept_req(user_id):
    res = db_manager.accept_req(user_id, current_user.id)
    if res is None:
        pass
    return redirect('/messenger')


@wsgi_app.route('/messenger/decline_req/<string:user_id>')
@login_required
def decline_req(user_id):
    res = db_manager.decline_req(user_id, current_user.id)
    if res is None:
        pass
    return redirect('/messenger')


@wsgi_app.route('/messenger', methods=['POST', 'GET'])
def messenger():
    if current_user.is_anonymous:
        return redirect('/login?page=/messenger')
    mes = None
    if request.method == 'POST':
        friend_name = request.form.get('Friend_Login')
        mes = db_manager.add_friend(current_user, friend_name)
    user_friends = db_manager.get_friends_for_user(current_user)
    user_requests = db_manager.get_friend_requests(current_user)
    return my_render_template('messenger.html', users=user_friends,
                              req=user_requests, message=mes)


@wsgi_app.route('/messenger/<user_id>', methods=['POST', 'GET'])
@login_required
def chat(user_id):
    friends = db_manager.get_friends_for_user(current_user)
    if db_manager.load_user(user_id) not in friends:
        return redirect('/messenger')
    if request.method == 'POST':
        message = request.form['message']
        db_manager.add_message(message, user_id, current_user.id)
    messages = db_manager.get_messages_for_users(current_user.id, user_id)
    user_friend = db_manager.load_user(user_id)
    return my_render_template('chat.html', messages=messages,
                              friend=user_friend, active_page='messanger')


@login_required
@wsgi_app.route('/account/edit', methods=['POST', 'GET'])
def account_edit():
    if request.method == 'POST':
        try:
            db_manager.edit_user(request.form)
        except IncorrectData as e:
            return my_render_template('edit_account.html', message=e,
                                      user=current_user)
        except Exception:
            # TODO: behavior
            return redirect('/')
        return redirect('/account')
    return my_render_template('edit_account.html', user=current_user)


@login_required
@wsgi_app.route('/account', methods=['POST', 'GET'])
def account():
    return my_render_template('account.html')


@wsgi_app.route('/cloud/edit_file/<file_path>', methods=['POST', 'GET'])
def edit_file(file_path):
    if current_user.is_anonymous:
        return redirect('/?page=/cloud')
    if request.method == 'POST':
        print(f'{file_path=}')
        print(f'{request.form=}')
        try:
            db_manager.edit_file(file_path, request.form)
        except Exception as e:
            return f'{e.__class__.__name__}\n{e}'
        return redirect('/cloud')
    file_to_edit = db_manager.find_file(current_user, file_path)
    if not file_to_edit:
        return redirect('/file_not_found')
    return my_render_template('file.html', file=file_to_edit,
                              link=f'https://{server_name}/cloud/'
                                   f'download/{file_to_edit.path}')


@wsgi_app.route('/light', methods=['POST'])
def light_theme():
    # try:
    #     print(current_user.theme)
    # except AttributeError:
    #     print('no theme')
    # current_user.theme = 1
    return redirect(request.args.get('url'))


@wsgi_app.route('/premium', methods=["POST", "GET"])
def premium():
    if request.method == "POST":
        return redirect("/get_premium")
    return my_render_template('premium.html')
