CREATE TABLE IF NOT EXISTS prop_photos (
prop_id VARCHAR (21) UNIQUE,
updated_at timestamp default now(),
photos JSONB,
street_view VARCHAR(128)
);
