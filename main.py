import hashlib
import os

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html') 


@app.route('/about')
def about():
    return "This is my site"


@app.route('/account', methods=['POST', 'GET'])
def account():
    if request.method == 'POST':
        print(request.form)
        name = request.form['Login']
        password = request.form['Password']
        user = User.query.filter_by(name=name).first()
        if user is None:
            return 'Nothing'
        key_from_db, salt = user.password, user.salt
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=128)
        if key_from_db == key:
            return 'Success'
        return 'Nothing'
    else:
        return render_template('login.html')


@app.route('/incorrect_password')
def incorrect_password():
    return render_template('nopassword.html')


@app.route('/success_register')
def success_register():
    return render_template('success_register.html')


@app.route('/users/<int:user_id>/<string:name>')
def user_page(user_id: int, name: str):
    # return f'You on the page of {name.capitalized()} with id {id_}'
    if user_id == 0 and name.lower() == 'lawrence':
        return 'The best lawrence!'
    return f'User was not found'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        print(request.form)
        name = request.form['Login']
        email = request.form['Email']
        password = request.form['Password']
        repeat_password = request.form['RepeatPassword']
        salt = os.urandom(32)
        if password != repeat_password:
            return redirect('/register')
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


if __name__ == "__main__":
    app.run(debug=True)
