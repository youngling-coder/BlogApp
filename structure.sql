CREATE TABLE IF NOT EXISTS users (
    userid SERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    postid SERIAL PRIMARY KEY,
    creator TEXT REFERENCES users(username),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    likes INTEGER NOT NULL DEFAULT 0
);


CREATE TABLE IF NOT EXISTS likes (
    likeid SERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL REFERENCES users(username),
    postid INTEGER NOT NULL REFERENCES posts(postid)
)
