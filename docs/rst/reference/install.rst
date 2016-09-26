install
=======

.. command::ansible-playbook install <galaxy_role>

*New in version 0.2*

The ``ansible-container install`` command installs a container-enabled role as
a new containerized service in your project.

A successful execution will modify your ``container.yml``, ``main.yml``, and
``requirements.yml`` files. See :ref:`container_enabled_roles` for more.
