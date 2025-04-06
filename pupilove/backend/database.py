import os
import mysql.connector

DB_IP = os.getenv("DB_IP")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT"))


class MySQLWrapper:
    def __init__(self, host: str, user: str, password: str, database: str, port: int):
        self.connection = mysql.connector.connect(
            host=host, user=user, password=password, database=database, port=port
        )

    def execute_select(self, query: str, params: tuple = ()) -> list:
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def execute_update(self, query: str, params: tuple = ()) -> int:
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows

    def __del__(self):
        if self.connection.is_connected():
            self.connection.close()


def get_db_connection():
    client = MySQLWrapper(
        host=DB_IP, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT
    )
    yield client
    del client
