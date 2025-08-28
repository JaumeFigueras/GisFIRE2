-- lightning.sql

CREATE TABLE lightning (
        lightning_id SERIAL NOT NULL,
        lightning_utc_date_time TIMESTAMP WITH TIME ZONE NOT NULL,
        data_provider_name VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        x_4326 FLOAT NOT NULL,
        y_4326 FLOAT NOT NULL,
        geometry_4326 geometry(POINT,4326) NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        meteocat_id INTEGER,
        meteocat_peak_current FLOAT,
        meteocat_chi_squared FLOAT,
        meteocat_ellipse_major_axis FLOAT,
        meteocat_ellipse_minor_axis FLOAT,
        meteocat_ellipse_angle FLOAT,
        meteocat_number_of_sensors INTEGER,
        meteocat_hit_ground BOOLEAN,
        meteocat_multiplicity INTEGER,
        meteocat_municipality_code VARCHAR,
        x_4258 FLOAT,
        y_4258 FLOAT,
        geometry_4258 geometry(POINT,4258),
        x_25831 FLOAT,
        y_25831 FLOAT,
        geometry_25831 geometry(POINT,25831),
        PRIMARY KEY (lightning_id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (data_provider_name)
)
WITH (
  OIDS = FALSE
);
ALTER TABLE public.lightning
  OWNER TO gisfire_user
;
GRANT ALL on public.lightning to gisfire_remoteuser;
CREATE INDEX lightning_utc_date_time_idx ON lightning (lightning_utc_date_time);
