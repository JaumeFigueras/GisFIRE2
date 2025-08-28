-- thunderstorm_experiment.sql

CREATE TYPE thunderstorm_experiment_algorithm_enum AS ENUM ('TIME', 'DISTANCE', 'TIME_DISTANCE', 'DBSCAN_TIME', 'DBSCAN_TIME_DISTANCE');

CREATE TABLE thunderstorm_experiment (
        thunderstorm_experiment_id SERIAL NOT NULL,
        thunderstorm_experiment_algorithm thunderstorm_experiment_algorithm_enum NOT NULL,
        thunderstorm_experiment_parameters HSTORE,
        data_provider_name VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        PRIMARY KEY (thunderstorm_experiment_id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (data_provider_name)
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.thunderstorm_experiment
  OWNER TO gisfire_user
;
GRANT ALL on public.thunderstorm_experiment to gisfire_remoteuser;
