from flask import render_template

from . import wsgi_app
from .data.db_manager import my_render_template


@wsgi_app.route('/premium')
def premium():
    return my_render_template('premium.html')


@wsgi_app.route('/about')
def about():
    return my_render_template('about.html')


@wsgi_app.route('/politic')
def politic():
    return my_render_template('politic.html')


@wsgi_app.route('/yandex_baf6d04d550034ad.html')
def yandex_check():
    return render_template('/yandex_baf6d04d550034ad.html')


@wsgi_app.route('/support')
def support():
    return my_render_template('support.html')


@wsgi_app.route('/file_not_found')
def file_not_found():
    return my_render_template('file_not_found.html')


@wsgi_app.route('/get_premium')
def get_premium():
    return my_render_template('get_premium.html', active_page='premium')



