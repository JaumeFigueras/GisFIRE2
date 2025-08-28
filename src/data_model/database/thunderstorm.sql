-- thunderstorm.sql

CREATE TABLE thunderstorm (
        thunderstorm_id SERIAL NOT NULL,
        thunderstorm_utc_date_time_start TIMESTAMP WITH TIME ZONE NOT NULL,
        thunderstorm_utc_date_time_end TIMESTAMP WITH TIME ZONE NOT NULL,
        thunderstorm_lightnings_per_minute FLOAT NOT NULL,
        thunderstorm_travelled_distance FLOAT NOT NULL,
        thunderstorm_cardinal_direction FLOAT NOT NULL,
        thunderstorm_speed FLOAT NOT NULL,
        thunderstorm_number_of_lightnings INTEGER NOT NULL,
        convex_hull_4326 geometry(POLYGON,4326),
        thunderstorm_experiment_id INTEGER NOT NULL,
        x_4326 FLOAT NOT NULL,
        y_4326 FLOAT NOT NULL,
        geometry_4326 geometry(POINT,4326) NOT NULL,
        type VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        x_4258 FLOAT,
        y_4258 FLOAT,
        geometry_4258 geometry(POINT,4258),
        x_25831 FLOAT,
        y_25831 FLOAT,
        geometry_25831 geometry(POINT,25831),
        convex_hull_4258 geometry(POLYGON,4258),
        convex_hull_25831 geometry(POLYGON,25831),
        PRIMARY KEY (thunderstorm_id),
        FOREIGN KEY(thunderstorm_experiment_id) REFERENCES thunderstorm_experiment (thunderstorm_experiment_id) ON DELETE CASCADE ON UPDATE CASCADE
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.thunderstorm
  OWNER TO gisfire_user
;
GRANT ALL on public.thunderstorm to gisfire_remoteuser;