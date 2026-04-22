import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="1234",
            database="year_project"
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
