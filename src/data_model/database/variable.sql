-- variable.sql

CREATE TYPE meteocat_variable_category AS ENUM ('DAT', 'AUX', 'CMV');

CREATE TABLE variable (
        variable_id SERIAL NOT NULL,
        variable_name VARCHAR NOT NULL,
        data_provider_name VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        meteocat_variable_code INTEGER NOT NULL,
        meteocat_variable_unit VARCHAR NOT NULL,
        meteocat_variable_acronym VARCHAR NOT NULL,
        meteocat_variable_category meteocat_variable_category NOT NULL,
        meteocat_variable_decimal_positions INTEGER NOT NULL,
        PRIMARY KEY (variable_id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (data_provider_name),
        UNIQUE (meteocat_variable_code)
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.variable
  OWNER TO gisfire_user
;
GRANT ALL on public.variable to gisfire_remoteuser;
