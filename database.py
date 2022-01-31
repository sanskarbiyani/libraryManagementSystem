import mysql.connector
from mysql.connector import errorcode
import os

DB_NAME = "library_management"


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
        string = f"SELECT ID FROM customer WHERE ID={userId}"
        self.cursor.execute(string)
        res = self.cursor.fetchall()
        print(res)
        return res

    def add_user(self, username, password):
        string = f"""INSERT INTO customer(customerName, Password) 
                VALUES ('{username}', '{password}')"""
        print(string)
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
            print(password)
            return password, cust_id
        except mysql.connector.Error as err:
            print(err)
