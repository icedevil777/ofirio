CREATE TABLE IF NOT EXISTS prop_events (
prop_id VARCHAR (20) UNIQUE,
parcel_number VARCHAR(80) DEFAULT NULL,
updated_at timestamp default now(),
mls_events JSONB,
price_change_events JSONB
);
