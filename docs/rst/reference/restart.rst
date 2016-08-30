restart
=======

**New in version 0.2.0**

.. program:: ansible-container restart [service [service ...]]

Restart containers for the services defined in *container.yml.* Optionally list one or more services to restart. The name of the service must match a service defined in
container.yml. If no services are specified, all services found in *container.yml* will be restarted.


