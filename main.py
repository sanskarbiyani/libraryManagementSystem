from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, UserMixin, logout_user
from dotenv import load_dotenv
from database import Database
import bcrypt
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = 'My name is Sanskar Biyani.'

login_manager = LoginManager()
login_manager.init_app(app)

mydb = Database()


class User(UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    print("Creating session.")
    user = User()
    user.id = user_id
    return user


@app.route("/")
def home_page():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        hashed, cust_id = mydb.get_password(username)
        if bcrypt.checkpw(str(password).encode('utf-8'), bytes(hashed)):
            print("Password Matched.")
            user = User()
            user.id = cust_id
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            print("Password not matching.")
        return 'None'


@app.route("/logout", methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/register", methods=['POST'])
def register():
    username = request.form['email']
    unhash = request.form['password']
    hashed_password = bcrypt.hashpw(
        str(unhash).encode('utf-8'), bcrypt.gensalt())
    mydb.add_user(username, hashed_password.decode())
    return "None"


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
