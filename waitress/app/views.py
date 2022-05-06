from flask import render_template

from . import app
from .data.db_manager import my_render_template


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


@app.route('/support')
def support():
    return my_render_template('support.html')


@app.route('/file_not_found')
def file_not_found():
    return my_render_template('file_not_found.html')


@app.route('/get_premium')
def get_premium():
    return my_render_template('get_premium.html', active_page='premium')



