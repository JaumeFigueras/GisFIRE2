-- lightning.sql

CREATE TABLE lightning (
        x_4326 FLOAT NOT NULL,
        y_4326 FLOAT NOT NULL,
        geometry_4326 geometry(POINT,4326) NOT NULL,
        date_time TIMESTAMP WITH TIME ZONE NOT NULL,
        tzinfo_date_time VARCHAR NOT NULL,
        id SERIAL NOT NULL,
        data_provider_name VARCHAR NOT NULL,
        type VARCHAR NOT NULL,
        ts TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
        meteocat_id INTEGER NOT NULL,
        meteocat_peak_current FLOAT NOT NULL,
        meteocat_chi_squared FLOAT NOT NULL,
        meteocat_ellipse_major_axis FLOAT NOT NULL,
        meteocat_ellipse_minor_axis FLOAT NOT NULL,
        meteocat_ellipse_angle FLOAT NOT NULL,
        meteocat_number_of_sensors INTEGER NOT NULL,
        meteocat_hit_ground BOOLEAN NOT NULL,
        meteocat_multiplicity INTEGER,
        meteocat_municipality_code VARCHAR,
        x_4258 FLOAT NOT NULL,
        y_4258 FLOAT NOT NULL,
        geometry_4258 geometry(POINT,4258) NOT NULL,
        x_25831 FLOAT NOT NULL,
        y_25831 FLOAT NOT NULL,
        geometry_25831 geometry(POINT,25831) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(data_provider_name) REFERENCES data_provider (name)
)
WITH (
  OIDS = FALSE
);
ALTER TABLE public.lightning
  OWNER TO gisfire_user
;
GRANT ALL on public.lightning to gisfire_remoteuser;
CREATE INDEX lightning_date_time_idx ON lightning (date_time);
