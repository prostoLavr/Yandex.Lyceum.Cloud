from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
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


@app.route('/password')
def password():
    return render_template('password.html')


@app.route('/incorrect_password')
def incorrect_password():
    return render_template('nopassword.html')


@app.route('/account')
def account():
    return render_template('some.html')


@app.route('/users/<int:user_id>/<string:name>')
def user_page(user_id: int, name: str):
    # return f'You on the page of {name.capitalized()} with id {id_}'
    if user_id == 0 and name.lower() == 'lawrence':
        return 'The best lawrence!'
    return f'User was not found'


@app.route('/register')
def register():
    return render_template('register.html')


if __name__ == "__main__":
    app.run(debug=True)
