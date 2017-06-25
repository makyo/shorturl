create table if not exists shorturls (
    id integer primary key autoincrement,
    shorturl text,
    destination text
);
