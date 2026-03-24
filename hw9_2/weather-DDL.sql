create table b6710545849.weather
(
    id     int auto_increment
        primary key,
    ts     timestamp default CURRENT_TIMESTAMP not null,
    lat    float                               not null,
    lon    float                               not null,
    sensor text                                not null,
    source text                                not null,
    value  text                                not null
);

create index ts
    on b6710545849.weather (ts);

