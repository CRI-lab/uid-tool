DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Data CASCADE;
DROP TABLE IF EXISTS Project;
DROP TABLE IF EXISTS Coastal6;

CREATE TABLE Users (
  user_id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  firstname VARCHAR(255) NOT NULL,
  lastname VARCHAR(255),
  password VARCHAR(255) NOT NULL
);

CREATE TABLE Project (
  project_id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  project_name VARCHAR(255) NOT NULL UNIQUE,
  code CHAR(2) NOT NULL
);

CREATE TABLE Data (
  data_id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  creator_id INTEGER NOT NULL,
  project_id_1 INT,
  project_id_2 INT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  data_name VARCHAR(255) NOT NULL UNIQUE,
  file_location VARCHAR(255) NOT NULL,
  coastal6 BOOLEAN,
  uid VARCHAR(16) NOT NULL UNIQUE,
  FOREIGN KEY (creator_id) REFERENCES Users (user_id),
  FOREIGN KEY (project_id_1) REFERENCES Project(project_id),
  FOREIGN KEY (project_id_2) REFERENCES Project(project_id)
);

CREATE TABLE Coastal6 (
  reference_id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
  data_id INT NOT NULL,
  FOREIGN KEY (data_id) REFERENCES Data(data_id)
);

INSERT INTO public.project(
	project_id, created, project_name, code)
	VALUES (1, '2023-08-08 11:02:29', 'test', 'TS');