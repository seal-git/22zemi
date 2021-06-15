DROP DATABASE IF EXISTS sample_db;
CREATE DATABASE sample_db;
USE sample_db;


DROP TABLE IF EXISTS sample_table;
CREATE TABLE sample_table (
    user_id INT NOT NULL PRIMARY KEY,
    user_name   VARCHAR(255) NOT NULL
);

LOAD DATA
    INFILE '/docker-entrypoint-initdb.d/sample.csv'
    INTO TABLE sample_table
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n';
