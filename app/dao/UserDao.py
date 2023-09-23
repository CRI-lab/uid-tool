from psycopg2.extensions import connection
from werkzeug.security import generate_password_hash

class User:
    __db = None
    __cursor = None


    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def fetch_user_by_id(self, user_id):
        self.__cursor.execute(
            'SELECT * FROM users WHERE user_id = %s', (user_id,)
        )
        user = self.cursor.fetchone()
        return user

    def create_user(self, user_info):
        self.__cursor.execute(
            "INSERT INTO users (email, firstname, lastname, password) VALUES (%s, %s, %s, %s)",
            (user_info["email"], user_info["firstname"], user_info["lastname"], generate_password_hash(user_info["password"])),
        )
        self.__db.commit()

    def fetch_user_by_email(self, user_email):
        self.__cursor.execute(
            "SELECT * FROM users WHERE email = %s", (user_email,))
        user = self.__cursor.fetchone()
        return user