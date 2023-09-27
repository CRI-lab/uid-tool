from psycopg2.extensions import connection
import csv
import io


class Data:
    __db = None
    __cursor = None
    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()

    def build_query(self, filters: dict):
        base_query = """
        SELECT data_id, data_name, u.firstname, u.lastname, d.created, d.data_location_type, d.data_description,
               d.data_location, invenio, u.email, p1.project_name as project1_name, 
               p2.project_name as project2_name, uid
        FROM public.data d 
        JOIN public.users u on d.creator_id=u.user_id
        JOIN project p1 ON d.project_id_1=p1.project_id 
        JOIN project p2 on d.project_id_2=p2.project_id
        """
        where_clauses = []
        params = {}

        # This one is used for the data curation form
        if "data_name_exclusive" in filters:
            where_clauses.append("data_name = %(data_name_exclusive)s")
            params["data_name_exclusive"] = filters["data_name_exclusive"]
        
        if "email" in filters and filters["email"] != "":
            where_clauses.append("u.email = %(email)s")
            params["email"] = filters["email"]
        
        # Needed to rename this one because this is used for filters
        if "data_name_match" in filters and filters["data_name_match"] != "":
            where_clauses.append("data_name ILIKE %(data_name_match)s")
            params["data_name_match"] = '%' + filters["data_name_match"] + '%'

        if "data_location_type" in filters and filters["data_location_type"] != "":
            where_clauses.append("d.data_location_type = %(data_location_type)s")
            params["data_location_type"] = filters["data_location_type"]

        if "from_date" in filters and filters["from_date"] != "":
            where_clauses.append("d.created >= %(from_date)s")
            params["from_date"] = filters["from_date"]

        if "to_date" in filters and filters["to_date"] != "":
            where_clauses.append("d.created <= %(from_date)s")
            params["to_date"] = filters["to_date"]

        if "invenio" in filters and filters["invenio"] != "":
            where_clauses.append("invenio = %(invenio)s")
            params["invenio"] = filters["invenio"]

        if "project" in filters and filters["project"] != "":
            where_clauses.append("(p1.project_id = %(project)s OR p2.project_id = %(project)s)")
            params["project"] = filters["project"]

        if "user_id" in filters and filters["user_id"] != "":
            where_clauses.append("user_id = %(user_id)s")
            params["user_id"] = filters["user_id"]

        if "uid" in filters and filters["uid"] != "":
            where_clauses.append("uid ILIKE %(uid)s" )
            params["uid"] = "%" + filters["uid"] + "%"
        
        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY d.created DESC"

        return base_query, params
        
    def fetch_data_table(self, filters: dict):
        query, params = self.build_query(filters)
        self.__cursor.execute(query, params)
        data = self.__cursor.fetchall()
        return data
    
    def fetch_data_by_name(self, name):
        name_check = {"data_name_exclusive": name}
        query, params = self.build_query(name_check)
        self.__cursor.execute(query, params)
        data = self.__cursor.fetchone()
        return data

    def fetch_data_by_id(self, id):
        query, params = self.build_query({"data_id = %s", (id,)})
        self.__cursor.execute(query, params)
        data = self.__cursor.fetchone()
        return data

    def fetch_last_data_id(self):
        self.__cursor.execute("SELECT data_id FROM data ORDER by data_id DESC LIMIT 1")
        data_id = self.__cursor.fetchone()
        return data_id
        
    def create_data(self, data_info: dict):
        user_id = data_info["user_id"]
        data_name = data_info["data_name"]
        project1_id = data_info["project1_id"]
        project2_id = data_info["project2_id"]
        data_description = data_info["data_description"]
        invenio = False if data_info.get("invenio") is None else True
        data_location_type= data_info["data_location_type"]
        data_location= data_info["data_location"]
        db_created = data_info["db_created"]
        uid = data_info["uid"]



        self.__cursor.execute(
            "INSERT INTO data (creator_id, project_id_1, project_id_2, created, data_name, data_description, data_location_type, data_location, invenio, uid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING data_id;",
            (
                user_id,
                project1_id,
                project2_id,
                db_created,
                data_name,
                data_description,
                data_location_type,
                data_location,
                invenio,
                uid,
            ),
        )
        self.__db.commit()

    def update_data(self, data_info: dict, data_id: int):
        data_name = data_info['data_name']
        data_description = data_info['data_description']
        data_location_type = data_info['data_location_type']
        data_location = data_info['data_location']
        invenio = data_info["invenio"]

        self.__cursor.execute(
            "UPDATE data"
            " SET data_name=%s, data_description=%s, data_location=%s, data_location_type = %s, invenio=%s"
            " WHERE data_id=%s",
            (data_name, data_description, data_location, data_location_type, invenio, data_id),
        )
        self.__db.commit()

    def remove_data(self, data_id: int):
        self.__cursor.execute(
            "DELETE FROM data WHERE data_id=%s", (data_id,)
        )
        self.__db.commit()

    def write_to_csv(self, rows):
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerows(rows)

        output.seek(0)
        return output.getvalue()