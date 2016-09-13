Accessing Roles
===============

.. contents:: Topics


From the file system
--------------------

Starting with version 0.2.0 Ansible Container provides the ability to add custom volumes to the Ansible Build Container
by using the ``--with-volumes`` option. So if you have roles already installed on the local file system, you can simply
mount the path to the build container.

For example, if roles are installed at /var/roles, the following will make the roles available inside the build container
as ``/roles``:

.. code-block:: bash

    $ ansible-container build --with-volumes /var/roles:/roles

For the roles to be accessed by Ansible Playbook, add an ``ansible.cfg`` file to the ``ansible`` directory, and set the
``roles_path``:

.. code-block:: bash

    [defaults]
    roles_path=/roles

In your ``main.yml`` playbook refer to roles by name. For example, if the role ``geerlingguy.apache`` is installed in /var/roles
locally, then the following will execute the role as part of ``main.yml``:

.. code-block:: yaml

    - name: Example play
      hosts: web
      roles:
        - name: Install apache
          role: geerlingguy.apache

.. note::

    If using Docker Machine, be aware that mounting paths outside fo the user's home directory to a container may
    require additional steps. For more details see the Docker tutorial, `Manage data in containers <https://docs.docker.com/engine/tutorials/dockervolumes/#/mount-a-host-directory-as-a-data-volume>`_.

.. note::

    If you choose to access locally installed roles using ``--with-volumes``, then you must include the same volumes for 
    the ``run`` and ``shipit`` commands as you did for ``build``. During these operations the ``main.yml`` playbook is
    accessed using the ``--list-hosts`` option to determine the list of hosts affected by the playbook. If roles cannot be
    accessed, Ansible Playbook will fail to parse ``main.yml``.


From Galaxy and version control
-------------------------------

Starting in version 0.2.0 Ansible Container will automatically install roles included in a ``requirements.yml`` file placed in
the ``ansible`` directory. If you are unfamiliar with ``requirements.yml``, see `Installing Multiple Roles From a File <http://docs.ansible.com/ansible/galaxy.html#installing-multiple-roles-from-a-file>`_.

The default ``roles_path`` is set to ``/etc/ansible/roles`` on the build container, and roles will be installed there. No special
changes are required in ``main.yml``. To run an installed role simply refer to it by name.
