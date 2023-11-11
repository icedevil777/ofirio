CREATE TABLE price_history (
    id integer NOT NULL,
    prop_id character varying(21),
    price integer,
    update_date timestamp without time zone DEFAULT now(),
    created_at timestamp without time zone DEFAULT now(),
    parcel_number character varying(80)
);
