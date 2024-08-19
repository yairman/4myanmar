CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    passkey TEXT,
    user_uuid TEXT UNIQUE
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    filename TEXT,
    filepath TEXT,
    timestamp DATETIME,
    upvotes INTEGER DEFAULT 0,
    downvotes INTEGER DEFAULT 0,
    user_uuid TEXT,
    isVotedByMe Bit DEFAULT 0,
    isDownvotedByMe Bit DEFAULT 0,
    FOREIGN KEY (user_uuid) REFERENCES users(user_uuid)
);

CREATE TABLE replies (
    id INTEGER PRIMARY KEY NOT NULL,
    reply_post_id INTEGER NOT NULL,
    reply TEXT NOT NULL,
    filename TEXT,
    filepath TEXT,
    timestamp DATETIME,
    upvotes INTEGER,
    downvotes INTEGER,
    user_uuid ,
    FOREIGN KEY (reply_post_id) REFERENCES posts(id),
    FOREIGN KEY (user_uuid) REFERENCES users(user_uuid)
);

CREATE TABLE upvoters (
    id INTEGER PRIMARY KEY NOT NULL,
    post_id INTEGER NOT NULL,
    upvoter TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE downvoters (
    id INTEGER PRIMARY KEY NOT NULL,
    post_id INTEGER NOT NULL,
    downvoter TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE user_posts (
    id INTEGER PRIMARY KEY NOT NULL,
    user_uuid TEXT,
    post_id INTEGER NOT NULL,
    FOREIGN KEY (user_uuid) REFERENCES users(user_uuid),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE gibbrish2 (
    isOkay Bitoasjkdfok
);
