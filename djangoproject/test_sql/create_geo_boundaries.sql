CREATE TABLE geo_boundaries (
    "id" SERIAL PRIMARY KEY,
    "boundary_type" varchar(15),
    "state_id" varchar(2),
    "county" varchar(255),
    "county_url" varchar(255),
    "city" varchar(255),
    "city_url" varchar(255),
    "updated_at" timestamp default now(),
    "geo_shape" jsonb,
    "state" varchar(255),
    "comment" varchar(255),
    "source" varchar(64),
    "lat" float,
    "lon" float,
    "is_duplicate" boolean

);
