-- api_request_log.sql

CREATE TABLE api_request_log (
        api_request_id SERIAL NOT NULL,
        api_request_endpoint VARCHAR NOT NULL,
        api_request_params HSTORE,
        api_request_http_status INTEGER NOT NULL,
        api_request_error_message VARCHAR,
        data_provider_name VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        PRIMARY KEY (api_request_id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (data_provider_name)
)
WITH (
  OIDS = FALSE
);
ALTER TABLE public.api_request_log
  OWNER TO gisfire_user
;
GRANT ALL on public.api_request_log to gisfire_remoteuser;
