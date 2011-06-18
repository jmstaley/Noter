-- turn on foreign keys
PRAGMA foreign_keys = ON;

drop table if exists notes;
create table notes (
    id integer primary key autoincrement,
    title string null,
    entry string  not null
);

drop table if exists tags;
create table tags (
    id integer primary key autoincrement,
    tag string unique not null
);

drop table if exists note_tags;
create table note_tags (
    id integer primary key autoincrement,
    note_id integer not null,
    tag_id integer not null,
    foreign key(note_id) references notes(id),
    foreign key(tag_id) references tags(id)
);

drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username string not null,
    pw_hash string not null
);
