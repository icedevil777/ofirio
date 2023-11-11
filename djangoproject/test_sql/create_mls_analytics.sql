CREATE TABLE mls_analytics(
    "id" INTEGER PRIMARY KEY,
    "update_date" timestamp without time zone,
    "state_id" VARCHAR(2),
    "county" VARCHAR(255),
    "city" VARCHAR (255),
    "city_url" VARCHAR (255),
    "zip" VARCHAR(5),
    "agg_type" VARCHAR(8),
    "prop_class" VARCHAR (8),
    "graph_name" VARCHAR(64),
    "data" JSONB,
    "prop_type2" VARCHAR(15)
);
