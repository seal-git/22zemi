DROP DATABASE IF EXISTS sample_db;
CREATE DATABASE sample_db;
USE sample_db;

DROP TABLE IF EXISTS sample_table;
CREATE TABLE sample_table
(
    id   INT(10),
    name VARCHAR(40)
);

INSERT INTO sample_table (id, name)
VALUES (1, "Nagaoka");
INSERT INTO sample_table (id, name)
VALUES (2, "Tanaka");

ALTER TABLE sample_table ADD PRIMARY KEY (id);

DROP TABLE IF EXISTS gutenberg_information;
CREATE TABLE gutenberg_information
(
    book_id       INT,
    title         VARCHAR(255),
    author        VARCHAR(255),
    editor        VARCHAR(255),
    date          VARCHAR(255),
    language      VARCHAR(255),
    character_set VARCHAR(255)
);

LOAD DATA
    INFILE '/docker-entrypoint-initdb.d/gutenberg_information.csv'
    INTO TABLE gutenberg_information
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\n';

ALTER TABLE gutenberg_information ADD PRIMARY KEY (book_id);

DROP TABLE IF EXISTS gutenberg_sentence;
CREATE TABLE gutenberg_sentence
(
    id       INT,
    book_id  INT,
    sentence LONGTEXT
);
LOAD DATA
    INFILE '/docker-entrypoint-initdb.d/gutenberg_sentence.csv'
    INTO TABLE gutenberg_sentence
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"' /*optionallyにすると文の内容によってはエラーが起きるので注意*/
    LINES TERMINATED BY '\n';

ALTER TABLE gutenberg_sentence ADD PRIMARY KEY (id);
