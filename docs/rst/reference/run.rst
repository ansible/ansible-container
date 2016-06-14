run
===

.. program:: ansible-container run

The ``ansible-container run`` command launches the container orchestrator and runs
your built containers with the configuration in your ``container.yml`` file. This is
analogous to ``docker-compose run``.

.. option:: --production

By default, any `dev_overrides` you specified in your ``container.yml`` will be
applied when running your containers. You may specify to run your containers with
the production configuration by using this flag.



