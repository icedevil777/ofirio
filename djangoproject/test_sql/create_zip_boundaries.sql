CREATE TABLE zip_boundaries (
    "id" SERIAL PRIMARY KEY,
    "state_id" varchar(2),
    "zip" varchar(5),
    "updated_at" timestamp default now(),
    "lat" float,
    "lon" float,
    "geo_shape" jsonb
);
