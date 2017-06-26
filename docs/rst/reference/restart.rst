restart
=======

.. program:: ansible-container restart [service [service ...]]

Restart containers. Optionally list one or more services to restart. The name of the service must match a service defined in ``container.yml``. If no services are specified, all services will be restarted.

.. option:: --production

By default, any `dev_overrides` specified in ``container.yml`` will be used and included in the orchestration playbook. Use this flag to ignore `dev_overrides`, and run containers using the production configuration. If containers were started using the `--production` option, then it's a good idea to use this option with the ``restart`` command.

.. option:: --roles-path ROLES_PATH

If using roles not found in the ``roles`` directory within the project, use this option to specify the local path containing the roles. The specified path will be mounted to the conductor container, making the roles available.


