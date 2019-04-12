create table if not exists shorturls (
    id integer primary key autoincrement,
    shorturl text,
    destination text
);

create table if not exists apikeys (
    key text not null
);

-- /api is reserved
insert into shorturls (shorturl) values ('api');
