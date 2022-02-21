from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<User {self.user_id}'


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html') 


@app.route('/about')
def about():
    return "This is my site"


@app.route('/login')
def login():
    return render_template('password.html')


@app.route('/incorrect_password')
def incorrect_password():
    return render_template('nopassword.html')


@app.route('/account')
def account():
    return render_template('some.html')


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
        if password != repeat_password:
            return redirect('/register')
        user = User(name=name, password=password, email=email)
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/success_register')
        except Exception as e:
            print(e.__class__.__name__)
            print(e)
            return "Не удалось добавить аккаунт! Повторите попытку позже :("
    else:
        return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
