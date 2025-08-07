DROP TABLE IF EXISTS files;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS productModels;


-- this is the schema for the files table, just like a file handling system
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    percentage INTEGER,
    progress TEXT,
    stamp TEXT NOT NULL UNIQUE,
    timeSpent TEXT,
    platforms TEXT DEFAULT 'coupang'
    -- uploaderID INTEGER NOT NULL,
    -- FOREIGN KEY (uploaderID) REFERENCES users(id)
);


-- this is the schema for the users table
-- CREATE TABLE users (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     username TEXT UNIQUE NOT NULL,
--     password TEXT NOT NULL,
--     email TEXT NOT NULL,
--     status TEXT NOT NULL,
--     created_at TEXT NOT NULL,
--     updated_at TEXT NOT NULL
-- );


-- this is the schema for the productModels table
-- CREATE TABLE productModels (
--     productID INTEGER PRIMARY KEY NOT NULL,
--     productName TEXT NOT NULL,
--     price INTEGER,
--     status TEXT NOT NULL,
--     momo_price INTEGER,
--     price_gap INTEGER,
--     Level1 TEXT,
--     Level2 TEXT,
--     Level3 TEXT,
--     PIC TEXT,
--     shopName TEXT,
--     shopID TEXT,
--     created_at TEXT,
--     updated_at TEXT,
--     updater TEXT NOT NULL,
--     FOREIGN KEY (updater) REFERENCES users(id)
-- );


-- CREATE TABLE files (
--     id int IDENTITY(1,1) PRIMARY KEY ,
--     filename varchar(255) NOT NULL,
--     status varchar(255) NOT NULL,
--     stamp varchar(255) NOT NULL UNIQUE
-- );