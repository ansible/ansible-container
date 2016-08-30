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

.. option:: --remove-orphans

Remove containers for services not defined in container.yml.

.. option:: -d, --detached

**New in version 0.2.0**

Run the application in detached mode. Containers will execute in the background. Use the ``docker ps`` command
to check container status. Use ``ansible-container stop`` to stop the containers.
