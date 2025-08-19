-- api_request_log.sql

CREATE TABLE api_request_log (
        id SERIAL NOT NULL,
        endpoint VARCHAR NOT NULL,
        params HSTORE,
        http_status INTEGER NOT NULL,
        error_message VARCHAR,
        data_provider_name VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (name)
)
WITH (
  OIDS = FALSE
);
ALTER TABLE public.api_request_log
  OWNER TO gisfire_user
;
GRANT ALL on public.api_request_log to gisfire_remoteuser;
