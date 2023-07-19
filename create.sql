DROP TABLE IF EXISTS USERS;

CREATE TABLE USERS (
    discord_id VARCHAR PRIMARY KEY
                       UNIQUE
                       NOT NULL,
    birthday    DATE NOT NULL
);