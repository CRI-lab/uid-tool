"""
This module provides a Project DAO class for interacting with a database table called 'project'.
"""
from psycopg2.extensions import connection
import psycopg2


class Project:
    """Project DAO."""

    __db = None
    __cursor = None

    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def fetch_projects(self):
        """Fetches all projects from the database."""
        try:
            self.__cursor.execute("SELECT * FROM project")
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching projects: ", e)
            return None

    def fetch_project_by_name(self, project_name):
        """Fetches projects by its name from the database."""
        try:
            self.__cursor.execute(
                "SELECT * FROM project WHERE project_name=%s", (project_name,)
            )
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching projects: ", e)
            return None

    def fetch_project_by_id(self, project_id):
        """Fetches a project from the database by its ID."""
        try:
            self.__cursor.execute(
                "SELECT * FROM project WHERE project_id=%s", (str(project_id))
            )
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching projects: ", e)
            return None

    def fetch_project_by_user(self, user_id):
        """Fetches projects associated with a given user."""
        base_query = """
                SELECT DISTINCT *
                FROM project p 
                JOIN userprojects up ON p.project_id=up.project_id
                WHERE up.user_id = %s
                """
        try:
            self.__cursor.execute(base_query, (str(user_id)))
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching projects: ", e)
            return None

    def create_project(self, project_info):
        """Creates a new project."""
        create_date = project_info["created"]
        project_name = project_info["project_name"]
        project_code = project_info["code"]
        finished = project_info["finished"]
        try:
            self.__cursor.execute(
                "INSERT INTO project(created, project_name, code, finished) VALUES(%s, %s, %s, %s) RETURNING project_id",
                (
                    create_date,
                    project_name,
                    project_code,
                    finished,
                ),
            )
            self.__db.commit()
            return self.__cursor.fetchone()[0]
        except psycopg2.Error as e:
            print("Error creating project: ", e)
            return None

    def update_project(self, project_info, project_id):
        """Updates a project."""
        project_name = project_info["project_name"]
        finished = project_info["finished"]
        try:
            self.__cursor.execute(
                "UPDATE project SET project_name=%s, finished=%s WHERE project_id=%s",
                (project_name, finished, project_id),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error updating project: ", e)

    def remove_project(self, project_id):
        """Removes a project."""
        try:
            self.__cursor.execute("DELETE FROM project WHERE project_id=%s", (project_id,))
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error removing project: ", e)

    def get_projects_from_id(self, project_id1, project_id2=None):
        """get project code from project id"""
        try:
            if project_id2 is not None:
                self.__cursor.execute(
                    "SELECT code FROM project WHERE project_id IN (%s, %s)",
                    (project_id1, project_id2),
                )
                project1_code, project2_code = self.__cursor.fetchall()
            else:
                self.__cursor.execute(
                    "SELECT code FROM project WHERE project_id = %s",
                    (project_id1,),
                )
                project1_code = self.__cursor.fetchone()
                project2_code = "XX"
        except psycopg2.Error as e:
            print("Error fetching projects:", e)
            return None, None
        return project1_code, project2_code
