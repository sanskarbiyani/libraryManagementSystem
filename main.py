from cgitb import reset
from functools import wraps
from flask import Flask, redirect, render_template, request, url_for, abort
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
    def __init__(self, user_id, is_member, is_librarian) -> None:
        super().__init__()
        self.id = user_id
        self.is_member = is_member
        self.is_librarian = is_librarian


def librarian_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_librarian != 1:
            return abort(403)
        else:
            return func(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    print("Inside Load User.")
    user_details = mydb.get_user(user_id)
    if len(user_details) == 0:
        return None
    else:
        curr_user_id, is_member, is_librarian = user_details[0]
        user = User(curr_user_id, is_member, is_librarian)
        return user


@app.route("/")
def home_page():
    return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        if request.method == 'GET':
            return render_template('login.html')
        else:
            username = request.form['username']
            password = request.form['password']
            hashed, cust_id = mydb.get_password(username)
            if bcrypt.checkpw(str(password).encode('utf-8'), bytes(hashed)):
                print('Password Matched.')
                user_details = mydb.get_user_by_username(username)
                if(len(user_details) == 0):
                    return redirect(url_for('login'))
                else:
                    user_id, is_member, is_librarian = user_details[0]
                user = User(user_id, is_member, is_librarian)
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                print("Password not matching.")
                return 'None'
    else:
        return redirect("dashboard")


@app.route("/logout", methods=['GET'])
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
    user_details = mydb.get_user_by_username(username)
    if(len(user_details) == 0):
        return redirect(url_for('login'))
    else:
        user_id, is_member, is_librarian = user_details[0]
    user = User(user_id, is_member, is_librarian)
    login_user(user)
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
@login_required
def dashboard():
    all_books = mydb.get_all_books()
    return render_template('dashboard.html', books=all_books)


@app.route("/book/<int:isbn>", methods=['GET'])
def get_book(isbn):
    book_detail = mydb.get_book_by_isbn(isbn)
    if(len(book_detail) == 0):
        abort(404)
    else:
        result = {}
        result["book"] = book_detail[0]
        result["reviews"] = mydb.get_reviews(isbn)
        print(result['reviews'])
        return render_template('book.html', result=result)


@app.route("/search", methods=['GET'])
@login_required
def search_book():
    book_name = request.form['bookname']
    if(book_name and len(book_name) > 0):
        res = mydb.search_book(book_name)
        return "Finding Book"


@app.route("/book/<int:isbn>/chapter/<int:chapter_no>", methods=['GET'])
@login_required
def get_chapter(isbn, chapter_no):
    chapter_text = mydb.get_chapter(isbn, chapter_no)
    if(len(chapter_text) > 0):
        return render_template('chapter.html', chapter=chapter_text[0])


@app.route("/admin")
@login_required
@librarian_only
def admin():
    return "Admin Page."


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
