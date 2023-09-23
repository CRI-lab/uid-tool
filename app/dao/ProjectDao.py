from psycopg2.extensions import connection

class Project:
    __db = None
    __cursor = None


    def __init__(self, db: connection):
        self.__db = db
        self.__cursor = self.__db.cursor()
    
    def fetch_projects(self):
        self.__cursor.execute("SELECT * FROM project")
        return self.__cursor.fetchall()
    
    def fetch_project_by_name(self, project_name):
        self.__cursor.execute("SLECT * FROM project WHERE project_name=%s", (project_name,)) 
        return self.__cursor.fetchone()

    def fetch_project_by_id(self, project_id):
        self.__cursor.execute("SLECT * FROM project WHERE project_id=%s", (project_id)) 
        return self.__cursor.fetchone()
    
    def create_project(self, project_info):
        project_name = project_info["project_name"]
        project_code = project_info["project_code"]
        finished = project_info["finished"]
        create_date = project_info["created_date"]
        self.__cursor.execute(
            "INSERT INTO project VALUES(%s, %s, %s, %s)",
            (create_date, project_name, project_code, finished,)
        )
        self.__db.commit()

    def update_project(self, project_info, project_id):
        project_name = project_info["project_name"]
        finished = project_info["finished"]
        self.__cursor.execute(
            "UPDATE project SET project_name=%s, finished=%s WHERE project_id=%s",
            (project_name, finished, project_id),
        )
        self.__db.commit()

    def delete_project(self, project_id):
        self.__cursor.execute(
            "DELETE FROM project WHERE project_id=%d", (project_id,)
        )
        self.__db.commit()

    def get_project_from_id(self, project1, project2=None):
        if project2 is not None:
            self.__cursor.execute(
                "SELECT code FROM project WHERE project_id=%s OR project_id=%s ",
                (project1, project2),
            )
            [[project1_code], [project2_code]] = self.__cursor.fetchall()
        else:
            self.__cursor.execute(
                "SELECT code FROM project WHERE project_id=%s",
                (project1),
            )
            [project1_code] = self.__cursor.fetchone()
            project2_code = "XX"
        return project1_code, project2_code
