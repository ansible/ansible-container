run
===

.. program:: ansible-container run

The ``ansible-container run`` command launches the container orchestrator and runs
the built containers with the configuration found in ``container.yml``. For docker
deploys, this is roughly analogous to ``docker-compose run``.

.. option:: --production

By default, any `dev_overrides` you specified in your ``container.yml`` will be
applied when running your containers. You may specify to run your containers with
the production configuration by using this flag.

.. option:: --remove-orphans

Remove containers for services not defined in container.yml.

.. option:: --with-variables WITH_VARIABLES [WITH_VARIABLES ...]

Define one or more environment variables in the Ansible Builder Container. Format each variable as a
key=value string.

.. option:: --with-volumes WITH_VOLUMES [WITH_VOLUMES ...]

Mount one or more volumes to the Ansible Builder Container. Specify volumes as strings using the Docker
volume format.

.. option:: --roles-path LOCAL_PATH

If you have Ansible roles in a local path other than your ``roles/`` directory that you wish to use
during your build/run/deploy, specify that path with this option.
