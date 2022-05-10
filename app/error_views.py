from . import app
from .data.db_manager import my_render_template


@app.errorhandler(404)
def page_error(error):
    return my_render_template('no_work_with_text.html', text='Страница не найдена  :('), 404


@app.errorhandler(400)
def request_error(error):
    return my_render_template('no_work_with_text.html', text='Ошибка запроса  :('), 400


@app.errorhandler(413)
def request_error(error):
    return my_render_template('no_work_with_text.html', text='Файл слишком большой :('), 413


@app.errorhandler(401)
def unauthorized_error(error):
    return my_render_template('no_work_with_text.html', text='Кажется вы не авторизованы :(')


@app.errorhandler(500)
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
def site_no_work(error):
    return my_render_template('no_work_with_text.html', text='Кажется на сайте случилась ошибка. '
                                                             'Скорее всего он слишком сильно загружен. '
                                                             'Повторите попытку позже  :('), 500
