CREATE DATABASE IF NOT EXISTS sample_db;
USE sample_db;

CREATE TABLE IF NOT EXISTS initial_db
(
  id    INT(10),
  name  VARCHAR(40)
);

INSERT INTO initial_db (id, name) VALUES (1, "Nagaoka");
INSERT INTO initial_db (id, name) VALUES (2, "Tanaka");
