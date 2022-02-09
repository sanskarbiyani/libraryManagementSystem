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
        string = f"""SELECT ID, Is_Member, Is_Librarian FROM customer WHERE customerName='{username}'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def add_user(self, username, password):
        string = f"""INSERT INTO customer(customerName, Password) 
                VALUES ('{username}', '{password}')"""
        try:
            self.cursor.execute(string)
        except mysql.connector.Error as err:
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
        string = f"""SELECT * FROM book WHERE Name LIKE '%{book_name}%'"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res

    def get_chapter(self, isbn, chapter):
        string = f"""SELECT * FROM chapter WHERE book_id={isbn} AND chapter_id={chapter}"""
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        return res
