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
        user = self.__cursor.fetchone()
        return user

    def create_user(self, user_info):
        self.__cursor.execute(
            "INSERT INTO users (email, firstname, lastname, role, password) VALUES (%s, %s, %s, %s, %s) RETURNING user_id",
            (user_info["email"], user_info["firstname"], user_info["lastname"], user_info["role"], generate_password_hash(user_info["password"])),
        )
        self.__db.commit()
        uid = self.__cursor.fetchone()
        return uid

    def fetch_user_by_email(self, user_email):
        self.__cursor.execute(
            "SELECT * FROM users WHERE email = %s", (user_email,))
        user = self.__cursor.fetchone()
        return user

    def fetch_user_emails(self):
        self.__cursor.execute(
            'SELECT email FROM users'
        )
        email = self.__cursor.fetchall()
        return email

    def assign_project(self, user_id, project_id):
        self.__cursor.execute(
            "INSERT INTO userprojects (user_id, project_id) VALUES (%s, %s)", (user_id, project_id,)
        )
        self.__db.commit()