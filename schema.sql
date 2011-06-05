drop table if exists notes;
create table notes (
    id integer primary key autoincrement,
    title string null,
    entry string  not null,
    tags string null
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username string not null,
    pw_hash string not null
);
