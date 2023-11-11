CREATE TABLE parsing_mls_mlsprovider (
    id integer NOT NULL,
    provider_name character varying(32) NOT NULL,
    state_id character varying(2) NOT NULL,
    endpoint character varying(255),
    comment character varying(512),
    transport character varying(6) NOT NULL,
    internal_name character varying(32),
    last_rent_load_ts timestamp with time zone,
    last_rent_process_ts timestamp with time zone,
    last_sales_load_ts timestamp with time zone,
    last_sales_process_ts timestamp with time zone
);
