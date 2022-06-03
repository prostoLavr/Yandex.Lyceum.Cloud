from . import wsgi_app
from .data.db_manager import my_render_template


@wsgi_app.errorhandler(404)
def page_error(error):
    return my_render_template('no_work_with_text.html', text='Страница не найдена  :('), 404


@wsgi_app.errorhandler(400)
def request_error(error):
    return my_render_template('no_work_with_text.html', text='Ошибка запроса  :('), 400


@wsgi_app.errorhandler(413)
def request_error(error):
    return my_render_template('no_work_with_text.html', text='Файл слишком большой :('), 413


@wsgi_app.errorhandler(401)
def unauthorized_error(error):
    return my_render_template('no_work_with_text.html', text='Кажется вы не авторизованы :(')


@wsgi_app.errorhandler(500)
@wsgi_app.errorhandler(502)
@wsgi_app.errorhandler(503)
@wsgi_app.errorhandler(504)
def site_no_work(error):
    return my_render_template('no_work_with_text.html', text='Кажется на сайте случилась ошибка. '
                                                             'Скорее всего он слишком сильно загружен. '
                                                             'Повторите попытку позже  :('), 500
