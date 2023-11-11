CREATE TABLE all_props (
    prop_id character varying(21),
    updated_at timestamp without time zone DEFAULT now(),
    prop_class character varying(8),
    listing_id character varying(32),
    source_mls character varying(60),
    list_date timestamp without time zone,
    close_date timestamp without time zone,
    list_price numeric,
    close_price numeric,
    status character varying(128),
    address_zip_line character varying(256),
    raw_prop_type character varying(128),
    deleted boolean DEFAULT false
);
