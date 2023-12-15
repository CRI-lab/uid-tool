"""
This module provides a Record DAO class for interacting with a database table called 'record'.
"""
import csv
import io
from datetime import datetime

import psycopg2
from psycopg2.extensions import connection


def build_query(filters: dict):
    """Builds a SQL query based on the provided filters."""
    base_query = """
    SELECT record_id, record_name, u.firstname, u.lastname, r.created, r.data_location_type, r.record_description,
           r.data_location, invenio, u.email, p1.project_name as project1_name, 
           p2.project_name as project2_name, uid
    FROM record r 
    JOIN users u on r.creator_id=u.user_id
    JOIN project p1 ON r.project_id_1=p1.project_id 
    JOIN project p2 on r.project_id_2=p2.project_id
    """
    where_clauses = []
    params = {}

    if "record_id" in filters:
        where_clauses.append("record_id = %(record_id)s")
        params["record_id"] = filters["record_id"]

    # This one is used for the record curation form
    if "record_name_exclusive" in filters:
        where_clauses.append("record_name = %(record_name_exclusive)s")
        params["record_name_exclusive"] = filters["record_name_exclusive"]

    if "email" in filters and filters["email"] != "":
        where_clauses.append("u.email = %(email)s")
        params["email"] = filters["email"]

    # Needed to rename this one because this is used for filters
    if "record_name_match" in filters and filters["record_name_match"] != "":
        where_clauses.append("record_name ILIKE %(record_name_match)s")
        params["record_name_match"] = "%" + filters["record_name_match"] + "%"

    if "data_location_type" in filters and filters["data_location_type"] != "":
        where_clauses.append("r.data_location_type = %(data_location_type)s")
        params["data_location_type"] = filters["data_location_type"]

    if "from_date" in filters and filters["from_date"] != "":
        where_clauses.append("r.created >= %(from_date)s")
        params["from_date"] = datetime.strptime(
            filters["from_date"], "%Y-%m-%d"
        ).replace(hour=23, minute=59)

    if "to_date" in filters and filters["to_date"] != "":
        where_clauses.append("r.created <= %(to_date)s")
        params["to_date"] = datetime.strptime(
            filters["to_date"], "%Y-%m-%d"
        ).replace(hour=23, minute=59)

    if "invenio" in filters and filters["invenio"] != "":
        where_clauses.append("invenio = %(invenio)s")
        params["invenio"] = filters["invenio"]

    if "project" in filters and filters["project"] != "":
        where_clauses.append(
            "(p1.project_id = %(project)s OR p2.project_id = %(project)s)"
        )
        params["project"] = filters["project"]

    if "user_id" in filters and filters["user_id"] != "":
        where_clauses.append("user_id = %(user_id)s")
        params["user_id"] = filters["user_id"]

    if "uid" in filters and filters["uid"] != "":
        where_clauses.append("uid ILIKE %(uid)s")
        params["uid"] = "%" + filters["uid"] + "%"

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    base_query += " ORDER BY r.created DESC"

    return base_query, params


def write_to_csv(rows):
    """Writes rows to a CSV file."""
    try:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerows(rows)

        output.seek(0)
        return output.getvalue()
    except IOError as e:
        print("I/O Error writing to CSV", str(e))
        return None
    except csv.Error as e:
        print("CSV Error writing to CSV", str(e))
        return None


class Record:
    """Record DAO."""

    __db = None
    __cursor = None

    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def fetch_record_table(self, filters: dict):
        """Fetches record from the database."""
        query, params = build_query(filters)
        try:
            self.__cursor.execute(query, params)
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching record", str(e))
            return None

    def fetch_record_by_name(self, name):
        """Fetches record by name."""
        name_check = {"record_name_exclusive": name}
        query, params = build_query(name_check)
        try:
            self.__cursor.execute(query, params)
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching record", str(e))
            return None

    def fetch_record_by_id(self, record_id):
        """Fetches record by id."""
        id_check = {"record_id": record_id}
        query, params = build_query(id_check)
        try:
            self.__cursor.execute(query, params)
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching record", str(e))
            return None

    def fetch_last_record_id(self):
        """Fetches the last record id."""
        try:
            self.__cursor.execute("SELECT record_id FROM record ORDER by record_id DESC LIMIT 1")
            return self.__cursor.fetchone()
        except psycopg2.Error as e:
            print("Error fetching record", str(e))
            return None

    def create_record(self, record_info: dict):
        """Creates a new record."""
        uid = record_info["uid"]
        user_id = record_info["user_id"]
        record_name = record_info["record_name"]
        project1_id = record_info["project1_id"]
        project2_id = record_info["project2_id"]
        record_description = record_info["record_description"]
        invenio = "invenio" in record_info
        data_location_type = record_info["data_location_type"]
        data_location = record_info["data_location"]
        db_created = record_info["db_created"]

        query = """
                INSERT INTO record (creator_id, project_id_1, project_id_2, created, record_name, record_description,
                data_location_type, data_location, invenio, uid)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING record_id;
                """
        values = (
            user_id,
            project1_id,
            project2_id,
            db_created,
            record_name,
            record_description,
            data_location_type,
            data_location,
            invenio,
            uid,
        )
        try:
            self.__cursor.execute(query, values)
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error creating record", str(e))

    def fetch_project_record(self, user_id):
        """Fetches project record."""
        base_query = """
        SELECT DISTINCT record_id, record_name, u.firstname, u.lastname, r.created, r.data_location_type, 
               r.record_description, r.data_location, invenio, u.email, p1.project_name as project1_name, 
               p2.project_name as project2_name, uid
        FROM record r 
        JOIN users u ON r.creator_id=u.user_id
        JOIN project p1 ON r.project_id_1=p1.project_id 
        JOIN project p2 ON r.project_id_2=p2.project_id
        JOIN userprojects up ON r.creator_id=up.user_id
        WHERE EXISTS (
            SELECT *
            FROM userprojects up2
            WHERE up2.user_id = %s
                AND (up2.project_id = r.project_id_1
                    OR up2.project_id = r.project_id_2)
        )
        """
        try:
            self.__cursor.execute(base_query, str(user_id))
            return self.__cursor.fetchall()
        except psycopg2.Error as e:
            print("Error fetching record", str(e))
            return None

    def update_record(self, record_info: dict, record_id: int):
        """Updates a record."""
        record_name = record_info["record_name"]
        record_description = record_info["record_description"]
        data_location_type = record_info["data_location_type"]
        data_location = record_info["data_location"]
        invenio = record_info["invenio"]

        try:
            self.__cursor.execute(
                "UPDATE record"
                " SET record_name=%s, record_description=%s, data_location=%s, data_location_type = %s, invenio=%s"
                " WHERE record_id=%s",
                (
                    record_name,
                    record_description,
                    data_location,
                    data_location_type,
                    invenio,
                    record_id,
                ),
            )
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error updating record", str(e))

    def remove_record(self, record_id: int):
        """Removes a record."""
        try:
            self.__cursor.execute("DELETE FROM record WHERE record_id=%s", (record_id,))
            self.__db.commit()
        except psycopg2.Error as e:
            print("Error removing record", str(e))
