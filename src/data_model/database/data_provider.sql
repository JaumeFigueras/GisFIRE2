-- data_provider.sql

CREATE TABLE data_provider (
        data_provider_name VARCHAR NOT NULL,
        data_provider_description VARCHAR NOT NULL,
        data_provider_url VARCHAR,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        PRIMARY KEY (data_provider_name)
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.data_provider
  OWNER TO gisfire_user
;
GRANT ALL on public.data_provider to gisfire_remoteuser;