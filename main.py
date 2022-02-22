import hashlib
import os
from waitress import serve
from werkzeug.utils import secure_filename

# url_for function is used by html pages
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = 'static/files'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False)
    salt = db.Column(db.LargeBinary(32), nullable=False)
    password = db.Column(db.LargeBinary(128), nullable=False)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<User {self.user_id}>'


class File(db.Model):
    file_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    path = db.Column(db.String(64), nullable=False)


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/account', methods=['POST', 'GET'])
def account():
    if request.method == 'POST':
        print(request.form)
        if request.files:
            return save_file(request.files['File'])
        else:
            return confirm_login(request.form['Login'], request.form['Password'])
    else:
        return render_template('login.html')


def save_file(file):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    render_template('account.html')


def confirm_login(name, password):
    print(f'{name=}, {password=}')
    user = User.query.first()
    if user is not None:
        key_from_db, salt = user.password, user.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        if key_from_db == key:
            files = File.query.all()
            return render_template('account.html', files=files)
    return render_template('login_error.html')


@app.route('/incorrect_password')
def incorrect_password():
    return render_template('login_error.html')


@app.route('/success_register')
def success_register():
    return render_template('success_register.html')


@app.route('/support')
def support():
    return render_template('support.html')

# @app.route('/users/<int:user_id>/<string:name>')
# def user_page(user_id: int, name: str):
#     # return f'You on the page of {name.capitalized()} with id {id_}'
#     if user_id == 0 and name.lower() == 'lawrence':
#         return 'The best lawrence!'
#     return f'User was not found'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        name = request.form['Login']
        email = request.form['Email']
        password = request.form['Password']
        repeat_password = request.form['RepeatPassword']

        if (name_in_db(name) or len(name) < 4 or password != repeat_password
                or not name.isidentifier() or len(password) < 4 or len(name) > 32
                or len(password) > 128):
            return redirect('/register')

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        user = User(name=name, password=key, email=email, salt=salt)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/success_register')
        except Exception as e:
            print('ERROR ADD REGISTERED USER TO DB')
            print(e.__class__.__name__)
            print(e)
            return "Не удалось добавить аккаунт! Повторите попытку позже :("
    else:
        return render_template('register.html')


def name_in_db(name: str):
    print(name, 'in', User.query.filter_by(name=name).all())
    return name in map(lambda x: x.name, User.query.filter_by(name=name).all())


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect('account')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>'''


if __name__ == "__main__":
    app.run(debug=True, port=8080)
    # serve(app, port=8080)
