from functools import wraps
from flask import Flask, redirect, render_template, request, url_for, abort, flash
from flask_login import LoginManager, current_user, login_required, login_user, UserMixin, logout_user
from dotenv import load_dotenv
from database import Database
import bcrypt
import os
import string
import random
import smtplib

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
        self.member = is_member
        self.librarian = is_librarian


def librarian_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.librarian != 1:
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
            print(hashed)
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
                flash('Invalid Credentials')
                return render_template('login.html')
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
    pass_confirm = request.form['conPassword']
    if(unhash != pass_confirm):
        flash("Passwords not Matching. Please try again")
        return redirect(url_for('login'))
    hashed_password = bcrypt.hashpw(
        str(unhash).encode('utf-8'), bcrypt.gensalt())
    age = request.form['age']
    print(f"Age: {age}")
    return_values = mydb.add_user(
        username, hashed_password.decode(), age)
    if(return_values):
        flash('Email already in use. Please login to continue.')
        return redirect(url_for('login'))
    user_details = mydb.get_user_by_username(username)
    if(len(user_details) == 0):
        return redirect(url_for('login'))
    else:
        user_id, is_member, is_librarian = user_details[0]
    user = User(user_id, is_member, is_librarian)
    login_user(user)
    return redirect(url_for('dashboard'))


@app.route("/dashboard")
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
    book_name = request.args.get('bookname')
    if(book_name and len(book_name) > 0):
        res = mydb.search_book(book_name)
        length = True if len(res) > 0 else False
        return render_template('dashboard.html', books=res, length=length)
    else:
        return redirect('dashboard')


@app.route("/genres")
def get_genre():
    genres = mydb.get_genres()
    return render_template("genres.html", genres=genres)


@app.route("/book/<int:isbn>/chapter/<int:chapter_no>", methods=['GET'])
@login_required
def get_chapter(isbn, chapter_no):
    chapter_text = mydb.get_chapter(isbn, chapter_no)
    mydb.add_book_to_library(isbn, current_user.id)
    if(len(chapter_text) > 0):
        return render_template('chapter.html', chapter=chapter_text[0])
    else:
        return abort(404)


@app.route("/genre/<int:genre_id>")
def get_genre_books(genre_id):
    res = mydb.get_genre_books(genre_id)
    return render_template('dashboard.html', books=res)


@app.route("/profile")
def profile():
    pass


@app.route("/addReview", methods=['POST'])
@login_required
def add_review():
    review = request.form['review']
    book_id = request.form['book_id']
    print(f"Book id: {book_id}\n Review: {review}")
    mydb.add_review(book_id, current_user.id, review)
    return redirect(url_for('get_book', isbn=book_id))


@app.route("/addBook", methods=['GET', 'POST'])
@login_required
@librarian_only
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        name = request.form['name']
        author = request.form['author']
        pubDate = request.form['pubDate']
        description = request.form['description']
        price = request.form['price']
        mydb.addBook(isbn, name, author, pubDate, description, price)
        return redirect(url_for('dashboard'))
    else:
        return render_template('addBook.html')


@ app.route("/addAdmin", methods=['GET', 'POST'])
@ login_required
@ librarian_only
def add_lib():
    if request.method == 'POST':
        name = request.form['email']
        age = request.form['age']
        sal = request.form['salary']
        gen = request.form['gender']
        mydb.addLib(name, age, sal, gen)
        res = ''.join(random.choices(string.ascii_uppercase +
                                     string.digits, k=20))
        user_id = mydb.get_user_by_username(name)[0][0]
        mydb.add_temp_form(res, user_id)
        link = f"http://{request.headers['HOST']}{url_for('change_password', res=res)}"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=os.getenv('MY_EMAIL'),
                             password=os.getenv('MY_PASSWORD'))
            connection.sendmail(from_addr=os.getenv('MY_EMAIL'), to_addrs=name,
                                msg=f"Subject: Set/Reset Password "
                                    f"\n\nYou can set your new password with the link\n{link}\n This is one time use only.")
        return redirect(url_for('dashboard'))
    else:
        return render_template("addLib.html")


@app.route("/forgotPassword", methods=['POST'])
def forgot_pw():
    username = request.form['username']
    res = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits, k=20))
    user_id = mydb.get_user_by_username(username)[0][0]
    mydb.add_temp_form(res, user_id)
    link = f"http://{request.headers['HOST']}{url_for('change_password', res=res)}"
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=os.getenv('MY_EMAIL'),
                         password=os.getenv('MY_PASSWORD'))
        connection.sendmail(from_addr=os.getenv('MY_EMAIL'), to_addrs=username,
                            msg=f"Subject: Set/Reset Password "
                                f"\n\nYou can set your new password with the link\n{link}\n This is one time use only.")
    flash("Link to Change Password sent.")
    return redirect("/login")


@app.route("/changePassword/<res>", methods=['GET', 'POST'])
def change_password(res):
    if request.method == 'POST':
        print(request.form)
        passwd = request.form['password']
        conPass = request.form['conPassword']
        email = request.form['email']
        if(passwd != conPass):
            flash("Passwords do not match.")
            return render_template('changePassword.html', email=email)
        else:
            user_details = mydb.get_user_by_username(email)
        if(len(user_details) == 0):
            return redirect(url_for('login'))
        else:
            user_id, is_member, is_librarian = user_details[0]

        hashed_password = bcrypt.hashpw(
            str(passwd).encode('utf-8'), bcrypt.gensalt())
        mydb.changePassword(user_id, hashed_password.decode())
        user = User(user_id, is_member, is_librarian)
        login_user(user)
        mydb.delete_from_res(res)
        return redirect(url_for('dashboard'))
    result = mydb.checkLinkPresen(res)
    if(len(result) > 0):
        email = mydb.getEmail(result[0][0])[0][0]
        return render_template('changePassword.html', email=email, link=res)
    return "Link Received."


@ app.route("/deleteBook/<int:isbn>", methods=['GET', 'POST'])
@ login_required
@ librarian_only
def delete_book(isbn):
    mydb.removeBook(isbn)
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
