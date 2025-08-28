-- thunderstorm_lightning_association.sql

CREATE TABLE thunderstorm_lightning_association (
        thunderstorm_id INTEGER NOT NULL,
        lightning_id INTEGER NOT NULL,
        PRIMARY KEY (thunderstorm_id, lightning_id),
        FOREIGN KEY(thunderstorm_id) REFERENCES thunderstorm (thunderstorm_id),
        FOREIGN KEY(lightning_id) REFERENCES lightning (lightning_id)
)
WITH (
  OIDS = FALSE
)
;
ALTER TABLE public.thunderstorm_lightning_association
  OWNER TO gisfire_user
;
GRANT ALL on public.thunderstorm_lightning_association to gisfire_remoteuser;
