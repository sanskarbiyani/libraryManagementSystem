import string
import mysql.connector
from mysql.connector import errorcode
import os

DB_NAME = "WTLLab"


class Database:
    def __init__(self) -> None:
        self.conn = mysql.connector.connect(
            host="localhost",
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWORD'),
            database=DB_NAME
        )
        self.cursor = self.conn.cursor()

    def get_user(self, userId):
        string = f"SELECT ID, is_member, is_librarian FROM customer WHERE ID={userId}"
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_user_by_username(self, username):
        print("Finding user.")
        string = f"""SELECT ID, Is_Member, Is_Librarian FROM customer WHERE customerName='{username}'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def add_user(self, username, password, age):
        print("Adding user")
        string = f"""INSERT INTO customer(customerName, Password, age) 
                VALUES ('{username}', '{password}', '{age}')"""
        try:
            self.cursor.execute(string)
        except mysql.connector.Error as err:
            if(err.errno == 1062):
                return "Username already Present"
            else:
                print(err)
        self.conn.commit()

    def get_password(self, username):
        string = f"""SELECT ID, Password FROM customer WHERE customerName='{username}'"""
        try:
            self.cursor.execute(string)
            res = self.cursor.fetchall()[0]
            cust_id = res[0]
            password = res[1]
            return password, cust_id
        except mysql.connector.Error as err:
            print(err)

    def get_all_books(self):
        string = f"""SELECT * from book"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_book_by_isbn(self, isbn):
        string = f"""SELECT * FROM book WHERE isbn='{isbn}'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_reviews(self, isbn):
        string = f"""SELECT r.review_text, c.customerName
                    FROM review as r
                    INNER JOIN customer AS c ON r.user_id = c.ID
                    INNER JOIN book AS b ON r.book_id = b.isbn
                    WHERE r.book_id={isbn}"""
        self.cursor.execute(string)
        res = self.cursor.fetchmany(size=10)
        return res

    def search_book(self, book_name):
        string = f"""SELECT isbn, Name, Author FROM book WHERE Name LIKE '%{book_name}%'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_chapter(self, isbn, chapter):
        string = f"""SELECT * FROM chapter WHERE book_id={isbn} AND chapter_id={chapter}"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_genres(self):
        string = f"""SELECT * FROM genre LIMIT 20"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_genre_books(self, genre_id):
        string = f"""SELECT b.isbn, b.Name, b.Author FROM genre_book as gb
                        INNER JOIN book AS b ON gb.book_id=b.isbn
                        WHERE gb.genre_id={genre_id}"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def add_review(self, book_id, user_id, review):
        string = f"""INSERT INTO review VALUES ('{book_id}', '{user_id}', '{review}')"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def addBook(self, isbn, name, author, pubDate, description, price):
        string = f"""INSERT INTO book (isbn, Name, Author, Date_Published, description, Price) VALUES
                    ('{isbn}', '{name}', '{author}', '{pubDate}', '{description}', '{price}')"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def addLib(self, name, age, salary, gender):
        string = f"""INSERT INTO customer (customerName, age, salary, gender, is_Librarian) VALUES
                        ('{name}', {age}, {salary}, {gender}, 1);"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def removeBook(self, isbn):
        string = f"""DELETE FROM book WHERE isbn='{isbn}';"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def add_temp_form(self, res, user_id):
        string = f"""INSERT INTO forgot_pw VALUES ({user_id}, '{res}')"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)

    def checkLinkPresen(self, res):
        string = f"""SELECT * FROM forgot_pw WHERE random_string='{res}'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def getEmail(self, user_id):
        string = f"""SELECT customerName FROM customer WHERE ID={user_id}"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def changePassword(self, user_id, password):
        string = f"""UPDATE customer SET password='{password}' WHERE ID='{user_id}'"""
        self.cursor.execute(string)
        self.conn.commit()

    def add_book_to_library(self, isbn, user_id):
        string = f"""INSERT INTO cust_book VALUES ({isbn}, {user_id}"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            if(err.errno == 1062):
                return
            else:
                print(err)

    def delete_from_res(self, res):
        string = f"""DELETE FROM forgot_pw WHERE random_string='{res}'"""
        try:
            self.cursor.execute(string)
            self.conn.commit()
        except mysql.connector.Error as err:
            print(err)
