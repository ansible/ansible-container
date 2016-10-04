run
===

.. program:: ansible-container run

The ``ansible-container run`` command launches the container orchestrator and runs
the built containers with the configuration found in ``container.yml``. This is
analogous to ``docker-compose run``.

.. note::

    Before starting the application containers, the build container is started, and Ansible Playbook is
    invoked with the ``--list-hosts`` option to inspect ``main.yml`` and return the list of hosts
    it touches. When entering the ``run`` command supply the same ``--with-volumes`` and
    ``--with-variables`` options passed to the``build`` command. This will ensure that ``main.yml``
    can be parsed and interpreted.

.. option:: -d, --detached

**New in version 0.2.0**

Run the application in detached mode. Containers will execute in the background. Use the ``docker ps`` command
to check container status. Use ``ansible-container stop`` to stop the containers.

.. option:: --production

By default, any `dev_overrides` you specified in your ``container.yml`` will be
applied when running your containers. You may specify to run your containers with
the production configuration by using this flag.

.. option:: --remove-orphans

Remove containers for services not defined in container.yml.

.. option:: --with-variables WITH_VARIABLES [WITH_VARIABLES ...]

**New in version 0.2.0**

Define one or more environment variables in the Ansible Builder Container. Format each variable as a
key=value string.

.. option:: --with-volumes WITH_VOLUMES [WITH_VOLUMES ...]

**New in version 0.2.0**

Mount one or more volumes to the Ansible Builder Container. Specify volumes as strings using the Docker
volume format.

.. option:: --roles-path LOCAL_PATH

**New in version 0.2.0**

If you have Ansible roles in a local path other than your `ansible/` directory that you wish to use
during your build/run/shipit, specify that path with this option.
