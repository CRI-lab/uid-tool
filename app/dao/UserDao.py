"""
This module provides a User DAO class for interacting with a database table called 'user'.
"""
from psycopg2.extensions import connection
from werkzeug.security import generate_password_hash
import psycopg2


class User:
    """User DAO."""

    __db = None
    __cursor = None

    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def fetch_user(self, user_id=None):
        """Fetches all users from the database."""
        query = "SELECT * FROM users"
        if user_id is not None:
            query += " WHERE user_id = %s"
        query += " ORDER BY user_id"
        try:
            self.__cursor.execute(query, str(user_id))
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching users: ", e)
            return None

    def create_user(self, user_info):
        """Creates a new user."""
        email = user_info["email"]
        firstname = user_info["firstname"]
        lastname = user_info["lastname"]
        role = user_info["role"]
        password = user_info["password"]
        try:
            self.__cursor.execute(
                "INSERT INTO users (email, firstname, lastname, role, password) VALUES (%s, %s, %s, %s, %s) RETURNING user_id",
                (email, firstname, lastname, role, generate_password_hash(password)),
            )
            self.__db.commit()
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error creating user: ", e)
            return None

    def fetch_user_by_email(self, user_email):
        """Fetches a user from the database by its email."""
        try:
            self.__cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching user: ", e)
            return None

    def fetch_user_emails(self):
        """Fetches all user emails from the database."""
        try:
            self.__cursor.execute("SELECT email FROM users")
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching users: ", e)
            return None

    def assign_project(self, user_id, project_id):
        """Assigns a project to a user."""
        try:
            self.__cursor.execute(
                "INSERT INTO userprojects (user_id, project_id) VALUES (%s, %s)",
                (
                    user_id,
                    project_id,
                ),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error assigning project: ", e)

    def unassign_project(self, user_id, project_id):
        """Unassigns a project from a user."""
        try:
            self.__cursor.execute(
                "DELETE FROM userprojects WHERE user_id=%s AND project_id=%s",
                (user_id, project_id),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error unassigning project: ", e)

    def remove_user(self, user_id):
        """Removes a user."""
        try:
            self.__cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error removing user: ", e)

    def update_user(self, user_info: dict, user_id: int):
        """Updates a user."""
        email = user_info["email"]
        firstname = user_info["firstname"]
        lastname = user_info["lastname"]
        role = user_info["role"]
        password = user_info["password"]

        params = {
            "email": email,
            "firstname": firstname,
            "lastname": lastname,
            "role": role,
            "user_id": user_id,
        }
        query = "UPDATE users SET email=%(email)s, firstname=%(firstname)s, lastname=%(lastname)s, role=%(role)s"

        if password != "":
            query += ", password=%(password)s"
            params["password"] = generate_password_hash(password)
            print("password updated")

        query += " WHERE user_id=%(user_id)s"

        try:
            self.__cursor.execute(query, params)
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error updating user: ", e)

    def fetch_user_projects(self, user_id: int):
        """Fetches user projects."""
        try:
            self.__cursor.execute(
                "SELECT up.project_id, p.project_name, p.code"
                " FROM userprojects up JOIN project p ON up.project_id=p.project_id"
                " WHERE user_id=%s",
                (str(user_id)),
            )
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching user projects: ", e)
            return None
