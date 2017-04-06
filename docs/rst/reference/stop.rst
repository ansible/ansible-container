stop
====

**New in version 0.2.0**

.. program:: ansible-container stop [service [service ...]]

Stop running containers for the services defined in *container.yml*.

Optionally, list one or more services to stop. The name of the service must match a service defined in
*container.yml*.

.. option:: -f, --force

Stop running containers by using the kill command.
