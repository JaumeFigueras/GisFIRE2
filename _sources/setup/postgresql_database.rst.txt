PostgreSQL Database
===================

**GisFIRE2** uses a `PostgreSQL <http://www.postgresql.org>`_ database the setup of the database follow the next steps:

1. Create an independent cluster

    .. code-block:: bash

      $ sudo pg_createcluster -d /home/postgresql-15/clusters/gisfire -l /home/postgresql-15/clusters/gisfire/gisfire.log -p 5433 --start --start-conf auto 15 gisfire

    **Important** Change the por (5433) to your preferred port

    .. note::

        It is possible, depending on the install that when creating the clusters appear an encoding error or warning.
        To solve this issue:

        .. code-block:: bash

         $ sudo locale-gen en_US en_US.UTF-8
         $ dpkg-reconfigure locales

        Then Select en_IE and en_US and set en_US as the default

2. Use the postgres user to setup the database inside the cluster

    .. code-block:: bash

      $ sudo -i -u postgres

3. Create the database and its users. The commands will promt to enter some information, the most impostant the
   password for easch user

    .. code-block:: bash

      $ createuser -p 5433 -P gisfire_user
      $ createuser -p 5433 -P gisfire_remoteuser
      $ createdb -p 5433 -E UTF8 -O gisfire_user gisfire_db

    Once the database is created enter to add the **HStore** and **PostGIS** extensions

    .. code-block:: bash

      $ psql -p 5433 -d gisfire_db

    Inside the SQL command line write.

    .. code-block:: sql

      create extension hstore;
      create extension postgis;

    To exit use :kbd:`Ctrl+D`

4. Allow external connection for the remote user (if needed)

    .. code-block:: bash

      $ nano /etc/postgresql/15/gisfire/pg_hba.conf

    Then add the following line trying to follow the tabulations of the file

    .. code-block::

      host all gisfire_remoteuser 0.0.0.0/0 scram-sha-256

    Then modify the configuration file to allow listening from other addresses than localhost

    .. code-block:: bash

      $ nano /etc/postgresql/15/gisfire/postgresql.conf

    Inside the file search and replace

    .. code-block::

      listen_addresses = '*'

    Once everythig is saved

    .. code-block::

      sudo systemctl status postgresql
      sudo systemctl restart postgresql
      sudo systemctl status postgresql

    So now your cluster is running and accepting remote connections