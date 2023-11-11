create table if not exists spin_text_cache (
    text_key varchar(255) primary key,
    variables jsonb
);
