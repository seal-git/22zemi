DROP SCHEMA IF EXISTS sample;
CREATE SCHEMA sample;
USE sample;
DROP TABLE IF EXISTS employee;

CREATE TABLE employee
(
  id    INT(10),
  name  VARCHAR(40)
);

INSERT INTO employee (id, name) VALUES (1, "Nagaoka");
INSERT INTO employee (id, name) VALUES (2, "Tanaka");
