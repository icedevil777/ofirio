CREATE TABLE parsing_mls_mlsconfig (
    id integer NOT NULL,
    mls_name character varying(128) NOT NULL,
    "user" character varying(128),
    password character varying(128),
    comment character varying(512),
    mls_provider_id integer NOT NULL,
    access_token character varying(128),
    feed_id character varying(128),
    originating_id character varying(128),
    originating_system character varying(128),
    disclosure_text character varying(128),
    logo_url character varying(128)
);
